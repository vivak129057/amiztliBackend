import os
import cloudinary
import cloudinary.uploader
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 1. Configuración directa con tus credenciales (sin usar .env temporalmente)
# ¡Coloca tus datos reales entre las comillas!
cloudinary.config(
    cloud_name="dvocywp3g",
    api_key="697285456284546",
    api_secret="CBnGpPh1slkKmyZwroGodH3PKUY"  # Reemplaza con tu API Secret real
)

CARPETA_DESTINO = 'uploads'
os.makedirs(CARPETA_DESTINO, exist_ok=True)

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '220682', # Tu contraseña actual
    'database': 'amiztli'
}

@app.route('/api/materiales_educativos', methods=['POST'])
def subir_material():
    try:
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion', '')
        condicion = request.form.get('condicion', '')
        archivo = request.files.get('archivo')

        if not archivo or archivo.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not titulo:
            return jsonify({'error': 'El título es obligatorio'}), 400

        # 1. Subimos el archivo a Cloudinary
        resultado = cloudinary.uploader.upload(archivo)
        url_archivo = resultado.get('secure_url')

        # 2. Obtenemos el nombre original del archivo
        nombre_archivo = archivo.filename

        # 3. Nos conectamos a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO materiales_educativos (titulo_recurso, descripcion, categoria, tipo_archivo, enlace_descarga)
            VALUES (%s, %s, %s, %s, %s)
        """
        # Guardamos el nombre en tipo_archivo y la URL en enlace_descarga
        valores = (titulo, descripcion, condicion, nombre_archivo, url_archivo)

        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'mensaje': '¡Material guardado exitosamente!', 'url': url_archivo}), 201

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/materiales_educativos', methods=['GET'])
def obtener_materiales():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id_materiales, titulo_recurso, descripcion, categoria, tipo_archivo, enlace_descarga FROM materiales_educativos ORDER BY id_materiales DESC")
        materiales = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(materiales), 200
    except Exception as e:
        return jsonify({'error': f'Error al leer la base de datos: {str(e)}'}), 500


@app.route('/abrir_archivo/<nombre_archivo>')
def abrir_archivo(nombre_archivo):
    return send_from_directory(CARPETA_DESTINO, nombre_archivo)


if __name__ == '__main__':
    app.run(port=5000, debug=True)