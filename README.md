## PetCare - Módulo de Citas Veterinarias y Facturación XML

Sistema web de gestión de citas veterinarias desarrollado bajo el patrón arquitectónico MVC, aplicando principios SOLID, patrones de diseño GoF (*Decorator*, *Factory Method*, *Adapter*), control de acceso por roles (RBAC) y persistencia relacional en SQLite.

## Requisitos Previos
Python 3.10 o superior instalado en el equipo.
Visual Studio Code.

## Pasos para Instalar y Ejecutar

1. Clonar o descargar el repositorio en su equipo local.
2. Abrir una terminal en la carpeta raíz del proyecto (`petcare_proyecto`) e instalar las librerías necesarias:
   ```bash
   pip install fastapi uvicorn streamlit pydantic
   
## Ejecutar la interfaz web principal de Streamlit con un comando a la vez:
cd OneDrive\Escritorio\petcare_proyecto (Por si la terminal no esta ubicada en la carpeta del proyecto, si lo esta, omitir este paso)
python -m streamlit run view_web.py

## El sistema abrirá automáticamente la aplicación web interactiva en el navegador en la dirección:
http://localhost:8501

## Para levantar de forma independiente el servidor de la API REST con FastAPI, puede ejecutar en otra terminal: 
uvicorn controller:app --reload

## Documentación de la API (Swagger / OpenAPI)
Una vez en ejecución el servidor de la API, la documentación interactiva generada automáticamente por Swagger se encuentra disponible en la siguiente URL:
http://localhost:8000/docs
