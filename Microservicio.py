from flask import Flask, jsonify, request
from pathlib import Path
from datetime import datetime
import mysql.connector


import asyncio
import time
from threading import Lock
from mysql.connector import Error

db = None
db_lock = Lock()

try:
    db = mysql.connector.connect(
        host="192.168.1.87",
        port=3306,
        user="server01",
        password="155167",
        database="manual",
        connection_timeout=5
    )

    if db.is_connected():
        print("Conexión exitosa con MySQL/MariaDB")

        cursor = db.cursor()
        cursor.execute("SELECT VERSION(), DATABASE()")

        resultado = cursor.fetchone()

        print("Versión del servidor:", resultado[0])
        print("Base de datos conectada:", resultado[1])

        cursor.close()

except Error as e:
    print(" Error al conectar:", e)


app = Flask(__name__)
elementos = []  
siguiente_id = 1

@app.route("/api/tabla001", methods=["GET"])
def leer_tabla001():
    if db is None:
        return jsonify({"error": "No hay conexión con la base de datos"}), 503

    try:
        with db_lock:
            db.ping(reconnect=True, attempts=3, delay=1)
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM table_01")
                filas = cursor.fetchall()
            finally:
                cursor.close()

        return jsonify(filas), 200
    except Error:
        app.logger.exception("Error al leer la tabla tabla001")
        return jsonify({"error": "No se pudo leer la tabla tabla001"}), 500

@app.route("/api/elementos", methods=["GET"])
def listar_elementos():
    return jsonify(elementos)

@app.route("/api/elementos/<int:elemento_id>", methods=["GET"])
def obtener_elemento(elemento_id):
    elemento = next((item for item in elementos if item["id"] == elemento_id), None)

    if elemento is None:
        return jsonify({"error": "Elemento no encontrado"}), 404

    return jsonify(elemento)

@app.route("/api/elementos/nombre/<elemento_nombre>", methods=["GET"])
def obtener_elemento_nombre(elemento_nombre):
    elemento = next((item for item in elementos if item["nombre"] == elemento_nombre), None)

    if elemento is None:
        return jsonify({"error": "Elemento no encontrado"}), 404

    return jsonify(elemento)

@app.route("/api/elementos", methods=["POST"])
async def crear_elemento():
    global siguiente_id
    inicio = datetime.now()
    datos = request.get_json()
    print(f"INICIO: {inicio} - solicitud recibida - {datos["nombre"]}")
    if not datos or "nombre" not in datos:
        return jsonify({"error": "Debes enviar un campo 'nombre'"}), 400

    nuevo_elemento = {
        "id": siguiente_id,
        "nombre": datos["nombre"],
        "direccion": datos["direccion"],
        "telefono": datos["telefono"]
    }
    
    elementos.append(nuevo_elemento)
    siguiente_id += 1
    await asyncio.sleep(10)
    fin = datetime.now()
    print(f"FIN: {fin} - solicitud terminada - {datos["nombre"]}")
    

    return jsonify(nuevo_elemento), 201

@app.route("/api/elementos/<int:elemento_id>", methods=["PUT"])
def actualizar_elemento(elemento_id):
    datos = request.get_json()
    elemento = next((item for item in elementos if item["id"] == elemento_id), None)

    if elemento is None:
        return jsonify({"error": "Elemento no encontrado"}), 404

    if not datos or "nombre" not in datos:
        return jsonify({"error": "Debes enviar un campo 'nombre'"}), 400

    elemento["nombre"] = datos["nombre"]
    return jsonify(elemento)

@app.route("/api/elementos/<int:elemento_id>", methods=["DELETE"])
def eliminar_elemento(elemento_id):
    elemento = next((item for item in elementos if item["id"] == elemento_id), None)

    if elemento is None:
        return jsonify({"error": "Elemento no encontrado"}), 404

    elementos.remove(elemento)
    return jsonify({"mensaje": "Elemento eliminado correctamente"})





if __name__ == "__main__":
    app.run(debug=True, port=5000)
