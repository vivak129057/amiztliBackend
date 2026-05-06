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
        tipo = request.form.get('tipo', '')

        if not nombre:
            return jsonify({'error': 'El nombre de la institución es obligatorio'}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO directorio_instituciones (nombre, ubicacion, tipo, telefono, correo_electronico, Descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (nombre, ubicacion, tipo, telefono, correo_electronico, Descripcion)

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


@app.route('/api/especialistas', methods=['POST'])
def subir_especialista():
    try:
        # Recibimos los datos enviados desde el formulario en JavaScript
        nombre = request.form.get('nombre')
        apellido_paterno = request.form.get('apellido_paterno', '')
        apellido_materno = request.form.get('apellido_materno')
        especialidad = request.form.get('especialidad', '')
        telefono = request.form.get('telefono', '')
        correo_electronico = request.form.get('correo_electronico', '')
        ubicacion_consultorio = request.form.get('ubicacion_consultorio', '')
        descripcion = request.form.get('Descripcion', '')
        experiencia_trastornos = request.form.get('experiencia_trastornos', '')

        # Validamos que los campos requeridos estén presentes
        if not nombre or not apellido_paterno or not especialidad:
            return jsonify({'error': 'Faltan campos obligatorios'}), 400

        # Nos conectamos a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO directorio_especialistas (
                nombre, apellido_paterno, apellido_materno, especialidad, 
                telefono, correo_electronico, ubicacion_consultorio, 
                Descripcion, experiencia_trastornos
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            nombre, apellido_paterno, apellido_materno, especialidad, 
            telefono, correo_electronico, ubicacion_consultorio, 
            descripcion, experiencia_trastornos
        )

        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'mensaje': '¡Especialista registrado exitosamente!'}), 201

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


@app.route('/api/especialistas', methods=['GET'])
def obtener_especialistas():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Leemos los datos de la base de datos
        cursor.execute("SELECT * FROM directorio_especialistas ORDER BY id_directorio_especialistas DESC")
        especialistas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(especialistas), 200
    except Exception as e:
        return jsonify({'error': f'Error al leer la base de datos: {str(e)}'}), 500


@app.route('/api/registro/especialista', methods=['POST'])
def registrar_especialista():
    try:
        nombre = request.form.get('nombre')
        especialidad = request.form.get('especialidad')
        cedula = request.form.get('cedula')
        ciudad = request.form.get('ciudad')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion', '')
        descripcion = request.form.get('descripcion', '')
        correo = request.form.get('correo')
        password = request.form.get('password')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO directorio_especialistas (
                nombre, especialidad, telefono, correo_electronico, 
                ubicacion_consultorio, Descripcion, trastornos_experiencia, 
                apellido_paterno -- Agregar según la lógica que tengas en tu BD
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Nota: Adapta los valores según la estructura de tu BD real.
        cursor.execute(sql, (nombre, especialidad, telefono, correo, ciudad, descripcion, "", ""))
        conn.commit()
        
        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Especialista registrado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registro/institucion', methods=['POST'])
def registrar_institucion():
    try:
        nombre = request.form.get('nombre')
        cct = request.form.get('cct')
        tipo = request.form.get('tipo')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        servicios = request.form.get('servicios')
        correo = request.form.get('correo')
        password = request.form.get('password')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO directorio_instituciones (
                nombre_institucion, tipo, direccion, telefono, 
                correo_electronico, Descripcion
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nombre, tipo, direccion, telefono, correo, servicios))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Institución registrada exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registro/maestro', methods=['POST'])
def registrar_maestro():
    try:
        nombre = request.form.get('nombre')
        nivel_educativo = request.form.get('nivel_educativo')
        estado = request.form.get('estado')
        escuela = request.form.get('escuela')
        intereses = request.form.get('intereses')
        correo = request.form.get('correo')
        password = request.form.get('password')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO datos_maestro (
                id_usuario, grado_estudios, institucion_afiliada, 
                materias_especialidad, anios_experiencia
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        # Se guarda el maestro. Ajusta si deseas crear el registro previo de usuario.
        cursor.execute(sql, (1, nivel_educativo, escuela, intereses, 0))
        conn.commit()
        
        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Maestro registrado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(port=port, debug=True)