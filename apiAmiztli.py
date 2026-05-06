import os
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()
import cloudinary
import cloudinary.uploader
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)

# Configuración de Cloudinary leyendo directo de las variables de entorno
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Configuración de la base de datos
db_config = {
    'host': os.getenv('MYSQLHOST'),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD'),
    'database': os.getenv('MYSQLDATABASE', 'railway'),
    'port': int(os.getenv('MYSQLPORT', '3306'))
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

        # 3. Nos conectamos a la base de datos de Railway
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO materiales_educativos (titulo_recurso, descripcion, categoria, tipo_archivo, enlace_descarga)
            VALUES (%s, %s, %s, %s, %s)
        """
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

@app.route('/api/instituciones', methods=['POST'])
def subir_institucion():
    try:
        nombre = request.form.get('nombre')
        ubicacion = request.form.get('ubicacion', '')
        telefono = request.form.get('telefono', '')
        correo_electronico = request.form.get('correo_electronico', '')
        Descripcion = request.form.get('Descripcion', '')

        if not nombre:
            return jsonify({'error': 'El nombre de la institución es obligatorio'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO directorio_instituciones (nombre, ubicacion, telefono, correo_electronico, Descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (nombre, ubicacion, telefono, correo_electronico, Descripcion)

        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'mensaje': '¡Institución registrada exitosamente!'}), 201

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

@app.route('/api/instituciones', methods=['GET'])
def obtener_instituciones():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM directorio_instituciones ORDER BY id_directorio_instituciones DESC")
        instituciones = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(instituciones), 200
    except Exception as e:
        return jsonify({'error': f'Error al leer la base de datos: {str(e)}'}), 500



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(port=port, debug=True)