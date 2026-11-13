from database import get_connection  # Importa la conexión a SQLite

class CitaRepository:
    
    @staticmethod
    def buscar_usuario(correo: str, clave: str):
        # Consulta si el correo y la contraseña coinciden en la BD
        conn = get_connection()
        user = conn.execute(
            "SELECT correo, rol FROM usuarios WHERE correo = ? AND clave = ?", 
            (correo, clave)
        ).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def contar_citas_medico(veterinario: str, fecha: str, hora: str) -> int:
        # Cuenta cuántas citas activas tiene el médico en esa misma fecha y hora
        conn = get_connection()
        fila = conn.execute("""
            SELECT COUNT(*) as total FROM citas 
            WHERE veterinario = ? AND fecha = ? AND hora = ? AND estado != 'Cancelada'
        """, (veterinario, fecha, hora)).fetchone()
        conn.close()
        return fila["total"]

    @staticmethod
    def crear(cita: dict) -> int:
        # Inserta una nueva cita y devuelve el ID generado
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO citas (mascota, propietario, veterinario, fecha, hora, motivo, tipo_consulta, estado, valor_pagado, xml_pago)
            VALUES (:mascota, :propietario, :veterinario, :fecha, :hora, :motivo, :tipo_consulta, :estado, :valor_pagado, :xml_pago)
        """, cita)
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        return nuevo_id

    @staticmethod
    def listar_todas() -> list:
        # Devuelve todas las citas registradas
        conn = get_connection()
        filas = conn.execute("SELECT * FROM citas ORDER BY fecha, hora").fetchall()
        conn.close()
        return [dict(f) for f in filas]

    @staticmethod
    def obtener_por_id(cita_id: int):
        # Busca una cita específica por su ID
        conn = get_connection()
        fila = conn.execute("SELECT * FROM citas WHERE id = ?", (cita_id,)).fetchone()
        conn.close()
        return dict(fila) if fila else None

    @staticmethod
    def actualizar_estado(cita_id: int, nuevo_estado: str) -> bool:
        # Actualiza el estado de una cita existente
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", (nuevo_estado, cita_id))
        conn.commit()
        actualizado = cursor.rowcount > 0
        conn.close()
        return actualizado

    @staticmethod
    def eliminar(cita_id: int) -> bool:
        # Elimina una cita de la base de datos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
        conn.commit()
        eliminado = cursor.rowcount > 0
        conn.close()
        return eliminado