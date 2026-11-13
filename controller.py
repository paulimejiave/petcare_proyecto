from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Literal
from database import init_db
from service import CitaService

# Inicializa la base de datos al arrancar la API
init_db()

# Crea la aplicación FastAPI (genera documentación Swagger automática en /docs)
app = FastAPI(title="PetCare API REST", description="Módulo de Citas Veterinarias y Pagos XML")

# Token de seguridad básico para proteger los endpoints
TOKEN_VALIDO = "petcare-token-secreto-2026"

def verificar_token(authorization: str = Header(None)):
    # Mecanismo de seguridad: exige el token en la cabecera Authorization
    if authorization != f"Bearer {TOKEN_VALIDO}":
        raise HTTPException(status_code=401, detail="No autorizado: Token inválido o ausente")

# Modelos Pydantic para validar datos de entrada automáticamente
class LoginInput(BaseModel):
    correo: str
    clave: str

class CitaInput(BaseModel):
    mascota: str = Field(..., min_length=2)
    propietario: str = Field(..., min_length=3)
    veterinario: str = Field(..., min_length=3)
    fecha: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # Valida formato YYYY-MM-DD
    hora: str = Field(..., pattern=r"^\d{2}:\d{2}$")          # Valida formato HH:MM
    motivo: str = Field(..., min_length=3)
    tipo_consulta: Literal["General", "Urgencia", "Especialista"]
    canal: Literal["Email", "WhatsApp"] = "Email"

class EstadoInput(BaseModel):
    estado: Literal["Pendiente", "Confirmada", "Completada", "Cancelada"]


# ENDPOINT 1: Inicio de sesión (Entrega el Token de seguridad)
@app.post("/api/login", status_code=200)
def login(datos: LoginInput):
    try:
        usuario = CitaService.iniciar_sesion(datos.correo, datos.clave)
        return {"usuario": usuario, "token": TOKEN_VALIDO}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# ENDPOINT 2: Consultar todas las citas (Protegido con Token)
@app.get("/api/citas", status_code=200, dependencies=[Depends(verificar_token)])
def listar_citas():
    return CitaService.consultar_citas()

# ENDPOINT 3: Crear / Agendar cita y generar pago XML (Protegido con Token)
@app.post("/api/citas", status_code=201, dependencies=[Depends(verificar_token)])
def crear_cita(cita: CitaInput):
    try:
        return CitaService.agendar_cita(cita.model_dump())
    except PermissionError as e:
        # Código 409 Conflict cuando el médico ya tiene ocupada esa fecha y hora
        raise HTTPException(status_code=409, detail=str(e))

# ENDPOINT 4: Actualizar estado de una cita (Protegido con Token)
@app.put("/api/citas/{cita_id}", status_code=200, dependencies=[Depends(verificar_token)])
def actualizar_cita(cita_id: int, datos: EstadoInput):
    try:
        CitaService.cambiar_estado(cita_id, datos.estado)
        return {"mensaje": "Estado actualizado correctamente"}
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ENDPOINT 5: Eliminar una cita (Protegido con Token)
@app.delete("/api/citas/{cita_id}", status_code=200, dependencies=[Depends(verificar_token)])
def eliminar_cita(cita_id: int):
    try:
        CitaService.eliminar_cita(cita_id)
        return {"mensaje": "Cita eliminada correctamente"}
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))