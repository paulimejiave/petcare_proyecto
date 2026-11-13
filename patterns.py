import xml.etree.ElementTree as ET  # Librería para construir documentos XML

# ==========================================
# 1. PATRÓN DECORATOR (Cálculo de Tarifas)
# ==========================================
class ConsultaBase:
    # Clase base con el precio estándar de la consulta veterinaria
    def calcular_costo(self) -> float:
        return 50000.0

class RecargoUrgencia(ConsultaBase):
    # Decorador que envuelve la consulta y le suma $30,000 por urgencia
    def __init__(self, consulta: ConsultaBase):
        self._consulta = consulta
    def calcular_costo(self) -> float:
        return self._consulta.calcular_costo() + 30000.0

class RecargoEspecialista(ConsultaBase):
    # Decorador que envuelve la consulta y le suma $40,000 por especialista
    def __init__(self, consulta: ConsultaBase):
        self._consulta = consulta
    def calcular_costo(self) -> float:
        return self._consulta.calcular_costo() + 40000.0


# ==========================================
# 2. PATRÓN FACTORY METHOD (Notificaciones)
# ==========================================
class NotificadorEmail:
    # Clase concreta para enviar recordatorios por correo
    def enviar(self, destino: str, mensaje: str) -> str:
        return f"Email enviado a {destino}: {mensaje}"

class NotificadorWhatsApp:
    # Clase concreta para enviar recordatorios por WhatsApp
    def enviar(self, destino: str, mensaje: str) -> str:
        return f"WhatsApp enviado a {destino}: {mensaje}"

class NotificadorFactory:
    # Fábrica que instancia el notificador correcto según lo que elija el usuario
    @staticmethod
    def crear(canal: str):
        if canal == "Email":
            return NotificadorEmail()
        if canal == "WhatsApp":
            return NotificadorWhatsApp()
        raise ValueError("Canal de notificación no soportado")


# ==========================================
# 3. PATRÓN ADAPTER (Sistema de Pagos XML)
# ==========================================
class AdaptadorFacturacionXML:
    # Adapta los datos de PetCare al formato XML que exige la API externa de pagos
    def __init__(self, propietario: str, mascota: str, tipo: str, total: float):
        self.propietario = propietario
        self.mascota = mascota
        self.tipo = tipo
        self.total = total

    def generar_factura_xml(self) -> str:
        # Construye las etiquetas XML del comprobante de pago
        raiz = ET.Element("FacturaElectronicaPetCare")
        ET.SubElement(raiz, "Propietario").text = self.propietario
        ET.SubElement(raiz, "Mascota").text = self.mascota
        ET.SubElement(raiz, "Servicio").text = self.tipo
        ET.SubElement(raiz, "ValorCOP").text = str(self.total)
        ET.SubElement(raiz, "EstadoPago").text = "APROBADO"
        return ET.tostring(raiz, encoding="unicode")