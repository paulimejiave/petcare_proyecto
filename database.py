import sqlite3  # Librería nativa de Python para bases de datos SQLite

DB_NAME = "PetCareDB.db"  # Nombre del archivo de la base de datos

def get_connection():
    # Abre la conexión a SQLite y permite acceder a las columnas por nombre
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Crea las tablas si aún no existen al iniciar el proyecto
    conn = get_connection()
    cursor = conn.cursor()
    
    # Activa la integridad referencial exigida en el documento
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Tabla de usuarios para el inicio de sesión (RBAC)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            correo TEXT PRIMARY KEY,
            clave TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)
    
    # Tabla principal de citas veterinarias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mascota TEXT NOT NULL,
            propietario TEXT NOT NULL,
            veterinario TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT NOT NULL,
            tipo_consulta TEXT NOT NULL,
            estado TEXT NOT NULL,
            valor_pagado REAL NOT NULL,
            xml_pago TEXT NOT NULL
        )
    """)
    
    # Inserta los 3 usuarios iniciales en la BD (no se muestran en la vista)
    usuarios = [
        ("admin@petcare.com", "admin123", "Administrador"),
        ("vet@petcare.com", "vet123", "Veterinario"),
        ("prop@petcare.com", "prop123", "Propietario")
    ]
    cursor.executemany("INSERT OR IGNORE INTO usuarios VALUES (?, ?, ?)", usuarios)
    
    conn.commit()  # Guarda los cambios en disco
    conn.close()   # Cierra la conexión