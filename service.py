from repository import CitaRepository
from patterns import ConsultaBase, RecargoUrgencia, RecargoEspecialista, NotificadorFactory, AdaptadorFacturacionXML

class CitaService:
    
    @staticmethod
    def iniciar_sesion(correo: str, clave: str):
        # Valida credenciales y retorna los datos del usuario si son correctos
        usuario = CitaRepository.buscar_usuario(correo, clave)
        if not usuario:
            raise ValueError("Correo o contraseña incorrectos")
        return usuario

    @staticmethod
    def agendar_cita(datos: dict) -> dict:
        # REGLA DE NEGOCIO NO TRIVIAL: Validar que el médico no tenga cruce de horario
        citas_existentes = CitaRepository.contar_citas_medico(
            datos["veterinario"], datos["fecha"], datos["hora"]
        )
        if citas_existentes > 0:
            # Lanza error de conflicto si el veterinario ya está ocupado
            raise PermissionError(f"El médico {datos['veterinario']} ya tiene cita el {datos['fecha']} a las {datos['hora']}")

        # Aplicar Patrón Decorator según el tipo de consulta
        consulta = ConsultaBase()
        if datos["tipo_consulta"] == "Urgencia":
            consulta = RecargoUrgencia(consulta)
        elif datos["tipo_consulta"] == "Especialista":
            consulta = RecargoEspecialista(consulta)
        valor_final = consulta.calcular_costo()

        # Aplicar Patrón Adapter para generar el XML de pago
        adaptador = AdaptadorFacturacionXML(
            datos["propietario"], datos["mascota"], datos["tipo_consulta"], valor_final
        )
        xml_factura = adaptador.generar_factura_xml()

        # Armar objeto completo para guardar en persistencia
        nueva_cita = {
            **datos,
            "estado": "Pendiente",
            "valor_pagado": valor_final,
            "xml_pago": xml_factura
        }
        cita_id = CitaRepository.crear(nueva_cita)

        # Aplicar Patrón Factory para generar la notificación
        notificador = NotificadorFactory.crear(datos.get("canal", "Email"))
        aviso = notificador.enviar(datos["propietario"], f"Cita #{cita_id} agendada para {datos['mascota']}")

        return {"id": cita_id, "valor_pagado": valor_final, "xml_pago": xml_factura, "notificacion": aviso}

    @staticmethod
    def consultar_citas() -> list:
        # Retorna el listado completo de citas
        return CitaRepository.listar_todas()

    @staticmethod
    def cambiar_estado(cita_id: int, nuevo_estado: str):
        # Valida que el estado sea permitido y actualiza la cita
        estados_validos = ["Pendiente", "Confirmada", "Completada", "Cancelada"]
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado no válido")
        if not CitaRepository.actualizar_estado(cita_id, nuevo_estado):
            raise LookupError("Cita no encontrada")

    @staticmethod
    def eliminar_cita(cita_id: int):
        # Elimina una cita verificando primero que exista
        if not CitaRepository.eliminar(cita_id):
            raise LookupError("Cita no encontrada para eliminar")