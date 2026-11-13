# Importación de la librería Streamlit para construir la interfaz gráfica web en localhost
import streamlit as st  

# Importación de la función para inicializar la base de datos SQLite
from database import init_db  

# Importación de la capa de lógica de negocio (MVC) que maneja las reglas y el repositorio
from service import CitaService  

# Ejecuta la función que crea la base de datos y las tablas si aún no existen
init_db()

# Configuración inicial de la ventana del navegador (título, ícono y diseño ancho)
st.set_page_config(page_title="PetCare - Citas Veterinarias", page_icon="🐾", layout="wide")

# Verificación en la memoria de la sesión si hay un usuario autenticado (inicialmente es None)
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ==========================================
# FUNCIONES DE VISTAS MODULARES (Principio DRY - Don't Repeat Yourself)
# ==========================================
def mostrar_lista_citas(permitir_eliminar: bool):
    """Función modular para mostrar la lista de citas, su XML y opciones de estado."""
    st.header("📋 Citas Agendadas en el Sistema")
    
    # Solicita a la capa de servicio todas las citas almacenadas en la base de datos
    citas = CitaService.consultar_citas()
    
    # Si no hay registros, muestra un aviso informativo al usuario
    if not citas:
        st.info("No hay citas registradas en la base de datos SQLite.")
        return

    # Recorre cada cita obtenida para mostrarla en un panel desplegable (expander)
    for c in citas:
        with st.expander(f"Cita #{c['id']} | Mascota: {c['mascota']} ({c['fecha']} - {c['hora']}) | Estado: [{c['estado']}]"):
            # Muestra los datos básicos del paciente y el médico asignado
            st.write(f"**Propietario:** {c['propietario']} | **Veterinario:** {c['veterinario']}")
            st.write(f"**Motivo:** {c['motivo']} | **Tipo de Atención:** {c['tipo_consulta']}")
            st.write(f"**Tarifa Liquidada (Patrón Decorator):** ${c['valor_pagado']:,.0f} COP")
            
            # Muestra el código XML generado mediante el Patrón Adapter
            st.markdown("**Comprobante de Pago Electrónico (Patrón Adapter XML):**")
            st.code(c["xml_pago"], language="xml")
            
            # Divide la vista en dos columnas para los botones de control operativo
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Actualizar Estado de la Cita (PUT):**")
                # Desplegable para seleccionar el nuevo estado operativo de la cita
                nuevo_est = st.selectbox(
                    "Seleccione nuevo estado", 
                    ["Pendiente", "Confirmada", "Completada", "Cancelada"],
                    index=["Pendiente", "Confirmada", "Completada", "Cancelada"].index(c["estado"]),
                    key=f"sel_{c['id']}"
                )
                # Botón que ejecuta la actualización del estado al hacer clic
                if st.button("Guardar Nuevo Estado", key=f"upd_{c['id']}"):
                    CitaService.cambiar_estado(c["id"], nuevo_est)
                    st.success("Estado actualizado correctamente en la base de datos.")
                    st.rerun() # Recarga la página para reflejar el cambio
            
            # Condicional estricto: Solo el Administrador tiene permiso para ver el botón de eliminar
            if permitir_eliminar:
                with col2:
                    st.markdown("**Eliminar Registro de Cita (DELETE):**")
                    if st.button("🗑️ Eliminar Cita", key=f"del_{c['id']}"):
                        CitaService.eliminar_cita(c["id"])
                        st.warning("Cita eliminada de la base de datos.")
                        st.rerun()

def mostrar_formulario_agendar():
    """Función modular que dibuja el formulario de agendamiento y aplica reglas de negocio."""
    st.header("➕ Agendamiento de Citas (Creación, Regla de Negocio y Facturación XML)")
    st.info("📌 **Regla de Negocio Activa:** El sistema bloquea automáticamente el registro si el veterinario seleccionado ya tiene una cita activa en la misma fecha y hora.")
    
    # Creación del formulario web para capturar los datos de la nueva cita
    with st.form("agendar_form"):
        mascota = st.text_input("Nombre de la Mascota")
        propietario = st.text_input("Nombre del Propietario")
        veterinario = st.selectbox("Veterinario Asignado", ["Dra. Laura Pérez", "Dr. Carlos Gómez", "Dr. Andrés Ruiz"])
        fecha = st.date_input("Fecha de la Cita").strftime("%Y-%m-%d")
        hora = st.selectbox("Hora de la Cita", ["08:00", "09:30", "11:00", "14:00", "15:30", "17:00"])
        motivo = st.text_input("Motivo de consulta")
        
        st.markdown("---")
        st.subheader("Aplicación de Patrones en el Agendamiento")
        # Selección para activar el Patrón Decorator (cálculo de tarifa)
        tipo = st.selectbox("Tipo de Consulta (Patrón Decorator - Cálculo de Tarifa)", ["General", "Urgencia", "Especialista"])
        # Selección para activar el Patrón Factory Method (canal de alerta)
        canal = st.selectbox("Canal de Notificación (Patrón Factory Method)", ["Email", "WhatsApp"])
        
        # Botón de envío del formulario
        if st.form_submit_button("Agendar Cita y Generar Factura XML"):
            # Validación simple de campos vacíos
            if not mascota or not propietario or not motivo:
                st.error("Por favor, complete todos los campos obligatorios.")
            else:
                try:
                    # Envía el diccionario con los datos a la capa de servicio
                    res = CitaService.agendar_cita({
                        "mascota": mascota, 
                        "propietario": propietario,
                        "veterinario": veterinario, 
                        "fecha": fecha,
                        "hora": hora, 
                        "motivo": motivo,
                        "tipo_consulta": tipo, 
                        "canal": canal
                    })
                    # Muestra mensajes de éxito con los resultados de los patrones
                    st.success(f"✅ Cita #{res['id']} creada con éxito. Valor total liquidado: ${res['valor_pagado']:,.0f} COP")
                    st.info(f"🔔 **Resultado Patrón Factory Method:** {res['notificacion']}")
                    st.markdown("📄 **Resultado Patrón Adapter (Factura XML Generada):**")
                    st.code(res["xml_pago"], language="xml")
                except PermissionError as e:
                    # Captura el error lanzado por la regla de negocio si hay cruce de horarios
                    st.error(f"⛔ Bloqueo por Regla de Negocio: {str(e)}")

def mostrar_patrones_gof():
    """Función modular que despliega la documentación teórica de los 3 patrones GoF."""
    st.header("🧩 Documentación y Demostración de Patrones de Diseño GoF")
    st.write("Esta sección evidencia los 3 patrones aplicados en la capa `patterns.py` del proyecto:")
    
    st.subheader("🔹 Patrón Estructural: Decorator (Cálculo Dinámico de Tarifas)")
    st.write("- **Problema que resuelve:** Permite sumar recargos económicos dinámicos por Urgencia (+$30,000) o Especialista (+$40,000) sobre una Consulta Base ($50,000) sin modificar el código original de la clase base.")
    st.write("- **Clases participantes:** `ConsultaBase`, `RecargoUrgencia`, `RecargoEspecialista`.")
    st.write("- **Principio SOLID asociado:** Open/Closed Principle (OCP).")
    
    st.markdown("---")
    
    st.subheader("🔹 Patrón Creacional: Factory Method (Emisión de Notificaciones)")
    st.write("- **Problema que resuelve:** Desacopla la lógica de negocio de la creación de alertas, instanciando dinámicamente el canal elegido (Email o WhatsApp).")
    st.write("- **Clases participantes:** `NotificadorFactory`, `NotificadorEmail`, `NotificadorWhatsApp`.")
    st.write("- **Principio SOLID asociado:** Single Responsibility Principle (SRP) y Dependency Inversion Principle (DIP).")
    
    st.markdown("---")
    
    st.subheader("🔹 Patrón Estructural: Adapter (Sistema de Pagos XML)")
    st.write("- **Problema que resuelve:** Adapta y traduce los datos internos de la cita médica al formato XML exigido por el sistema externo de facturación.")
    st.write("- **Clases participantes:** `AdaptadorFacturacionXML`.")
    st.write("- **Principio SOLID asociado:** Interface Segregation Principle (ISP).")


# ==========================================
# PANTALLA 1: INICIO DE SESIÓN (LOGIN LIMPIO)
# ==========================================
if st.session_state.usuario is None:
    st.title("🐾 PetCare - Sistema de Gestión de Citas Veterinarias")
    st.markdown("### Control de Acceso al Sistema (RBAC)")
    st.write("Ingrese sus credenciales institucionales para continuar.")
    
    # Formulario de autenticación (las contraseñas se ocultan con type='password')
    with st.form("login_form"):
        correo = st.text_input("Correo institucional")
        clave = st.text_input("Contraseña", type="password")
        entrar = st.form_submit_button("Iniciar Sesión")
        
        if entrar:
            try:
                # Valida las credenciales llamando al servicio y guarda el usuario en la sesión
                st.session_state.usuario = CitaService.iniciar_sesion(correo, clave)
                st.rerun() # Actualiza la interfaz para mostrar el panel correspondiente
            except ValueError as e:
                st.error(str(e))

# ==========================================
# PANTALLA 2: PANEL PRINCIPAL DIFERENCIADO POR ROL
# ==========================================
else:
    # Almacena en una variable los datos del usuario logueado actualmente
    user = st.session_state.usuario
    
    # Muestra en la barra lateral el rol y correo del usuario activo
    st.sidebar.title("🐾 PetCare MVC")
    st.sidebar.success(f"Rol activo: {user['rol']}")
    st.sidebar.write(f"Usuario: {user['correo']}")
    
    # Botón para destruir la sesión y volver al login
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()

    st.title("🏥 Módulo de Citas Veterinarias y Pagos XML - PetCare")
    
    # 1. VALIDACIÓN DE ROL: ADMINISTRADOR (Ve TODO)
    if user["rol"] == "Administrador":
        tabs = st.tabs([
            "📋 Consultar y Gestionar Citas (CRUD)", 
            "➕ Agendar Cita (Regla de Negocio + Pagos XML)", 
            "🧩 Patrones de Diseño GoF (Decorator, Factory, Adapter)"
        ])
        with tabs[0]:
            mostrar_lista_citas(permitir_eliminar=True) # El Admin sí puede eliminar
        with tabs[1]:
            mostrar_formulario_agendar()
        with tabs[2]:
            mostrar_patrones_gof()

    # 2. VALIDACIÓN DE ROL: VETERINARIO (Ve únicamente las citas y su gestión de estados)
    elif user["rol"] == "Veterinario":
        mostrar_lista_citas(permitir_eliminar=False) # El Veterinario NO puede eliminar

    # 3. VALIDACIÓN DE ROL: PROPIETARIO (Únicamente puede agendar citas)
    else:
        mostrar_formulario_agendar()