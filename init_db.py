# init_db.py
import sqlite3
import os

# Define la ruta a la base de datos dentro de la carpeta 'instance'
# Asegúrate de que la carpeta 'instance' exista
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(DB_DIR, 'el_receso.db')

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

print(f"Creando base de datos en: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Tabla de Usuarios (Necesaria para el Login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'estudiante' -- Roles: admin, empleado, estudiante
        )
    """)

    # 2. Tabla de Menú (Para la Cafetería)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL -- Ej: Desayuno, Almuerzo, Snacks
        )
    """)

    # Insertar un usuario Administrador de prueba (Contraseña: adminpass)
    # NOTA: En la app.py, Bcrypt se encarga de hashear la contraseña
    # Aquí solo la creamos para que el script no falle, aunque no usaremos esta inserción directa.
    # En la práctica, te registrarás desde el formulario.

    print("Tablas creadas exitosamente: user y menu.")
    conn.commit()
    conn.close()

except Exception as e:
    print(f"Ocurrió un error al inicializar la base de datos: {e}")

# Instrucción: Ejecuta este script UNA SOLA VEZ para crear la DB.
# python init_db.py