import streamlit as st
from streamlit.components.v1 import html as render_html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from PIL import Image
import os

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Firebay - Monitoreo de Incendios",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS PERSONALIZADOS
# ============================================================================
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem; 
        padding-left: 1rem; 
        padding-right: 1rem; 
    }

    .main-header {
        font-size: 3rem; 
        font-weight: 800;
        color: #B31B1B;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.3rem;
        color: #444; 
        text-align: center;
        margin-bottom: 2.5rem; 
        font-style: italic;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px; 
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e9ecef;
        border-radius: 8px 8px 0 0;
        padding: 12px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid #ced4da;
    }
    .stTabs [aria-selected="true"] {
        background-color: #B31B1B;
        color: white;
        border-color: #B31B1B;
        border-bottom: 2px solid white;
    }

    .sidebar-info {
        background-color: #f8d7da;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #721c24;
        margin-bottom: 1.5rem;
        color: #721c24;
    }

    iframe {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def generar_mapa_windy(latitud, longitud, zoom_level, capa_overlay):
    """Genera el iframe del mapa de Windy"""
    url_windy = (
        "https://embed.windy.com/embed2.html?"
        f"lat={latitud}&lon={longitud}&zoom={zoom_level}&overlay={capa_overlay}"
        "&menu=&message=true&marker=&calendar=&pressure=&type=map&location=coordinates"
    )

    codigo_iframe = f"""
    <iframe 
        width="100%" 
        height="600" 
        src="{url_windy}" 
        frameborder="0" 
        allowfullscreen="true"
        style="border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.15);">
    </iframe>
    """
    return codigo_iframe, url_windy

def generar_datos_historicos(inicio, fin, temp_base=25, hum_base=50):
    """Genera datos históricos simulados"""
    fechas = pd.date_range(start=inicio, end=fin, freq='D')
    n_days = len(fechas)

    datos = pd.DataFrame({
        'Fecha': fechas,
        'NDVI': 0.7 - (fechas - fechas[0]).days * 0.01 + np.random.uniform(-0.05, 0.05, n_days),
        'Temperatura': temp_base + np.array([i % 10 for i in range(n_days)]) + np.random.uniform(-2, 2, n_days),
        'Humedad': hum_base - np.array([i % 15 for i in range(n_days)]) + np.random.uniform(-5, 5, n_days),
        'Riesgo': 30 + (fechas - fechas[0]).days * 1.5 + np.random.uniform(-5, 5, n_days)
    })

    # Asegurar límites
    datos['NDVI'] = datos['NDVI'].clip(0, 1)
    datos['Humedad'] = datos['Humedad'].clip(0, 100)
    datos['Riesgo'] = datos['Riesgo'].clip(0, 100)

    return datos

def calcular_nivel_riesgo(temp, humedad, ndvi, ndmi, temp_threshold, hum_threshold, ndvi_threshold, ndmi_threshold):
    """Calcula el nivel de riesgo basado en los umbrales configurables"""
    puntos = 0

    # Temperatura (mayor temperatura = mayor riesgo)
    if temp > temp_threshold:
        puntos += 25
    elif temp > temp_threshold - 5:
        puntos += 15

    # Humedad (menor humedad = mayor riesgo)
    if humedad < hum_threshold:
        puntos += 25
    elif humedad < hum_threshold + 10:
        puntos += 15

    # NDVI (menor vegetación = mayor riesgo)
    if ndvi < ndvi_threshold:
        puntos += 25
    elif ndvi < ndvi_threshold + 0.15:
        puntos += 15

    # NDMI (menor humedad en vegetación = mayor riesgo)
    if ndmi < ndmi_threshold:
        puntos += 25
    elif ndmi < ndmi_threshold + 0.1:
        puntos += 15

    return min(puntos, 100)

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================
st.markdown('<div class="main-header">🔥 FIREBAY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema Inteligente de Prevención y Monitoreo de Incendios Forestales<br>Región de Aysén - Bahía Exploradores, Chile</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - PANEL DE CONTROL
# ============================================================================
with st.sidebar:
    st.image("images/Bosque.jpg", use_container_width=True)

    st.markdown("---")

    st.markdown("### 🎛️ Controles Principales")

    st.markdown("#### ⚠️ Umbrales de Alerta")
    umbral_ndvi = st.slider("Umbral NDVI crítico", 0.0, 1.0, 0.3, 0.05, help="Índice de vegetación normalizado (valores bajos = alerta)")
    umbral_ndmi = st.slider("Umbral NDMI crítico", -1.0, 1.0, 0.1, 0.05, help="Índice de humedad de la vegetación (valores bajos = mayor estrés hídrico)")
    umbral_mirbi = st.slider("Umbral MIRBI crítico", 0.0, 1.0, 0.3, 0.05, help="Índice de áreas quemadas (valores altos = alerta)")

    col_temp, col_hum = st.columns(2)
    with col_temp:
        umbral_temperatura = st.slider("Temp. Crítica (°C)", 25, 45, 35, 1)
    with col_hum:
        umbral_humedad = st.slider("Hum. Crítica (%)", 10, 50, 25, 5)

# ============================================================================
# CÁLCULOS DINÁMICOS BASADOS EN UMBRALES
# ============================================================================

# Valores actuales simulados
temp_actual = 32
humedad_actual = 28
ndvi_actual = 0.45
ndmi_actual = 0.15
mirbi_actual = 0.38

# Calcular riesgo dinámicamente
riesgo_calculado = calcular_nivel_riesgo(
    temp_actual, humedad_actual, ndvi_actual, ndmi_actual,
    umbral_temperatura, umbral_humedad, umbral_ndvi, umbral_ndmi
)

# Determinar nivel de riesgo basado en el cálculo
if riesgo_calculado >= 75:
    nivel_riesgo = "CRÍTICO"
    color_riesgo = "🔥"
elif riesgo_calculado >= 50:
    nivel_riesgo = "ALTO"
    color_riesgo = "⚠️"
elif riesgo_calculado >= 25:
    nivel_riesgo = "MEDIO"
    color_riesgo = "⚡"
else:
    nivel_riesgo = "BAJO"
    color_riesgo = "✅"

# Calcular alertas activas comparando con umbrales
alertas_activas = 0
alertas_detalle = []

if temp_actual > umbral_temperatura:
    alertas_activas += 1
    alertas_detalle.append(f"🌡️ Temperatura: {temp_actual}°C > {umbral_temperatura}°C")

if humedad_actual < umbral_humedad:
    alertas_activas += 1
    alertas_detalle.append(f"💧 Humedad: {humedad_actual}% < {umbral_humedad}%")

if ndvi_actual < umbral_ndvi:
    alertas_activas += 1
    alertas_detalle.append(f"🌿 NDVI: {ndvi_actual:.2f} < {umbral_ndvi:.2f}")

if ndmi_actual < umbral_ndmi:
    alertas_activas += 1
    alertas_detalle.append(f"💦 NDMI: {ndmi_actual:.2f} < {umbral_ndmi:.2f}")

if mirbi_actual > umbral_mirbi:
    alertas_activas += 1
    alertas_detalle.append(f"🔥 MIRBI: {mirbi_actual:.2f} > {umbral_mirbi:.2f}")


# ============================================================================
# DASHBOARD PRINCIPAL - MÉTRICAS CLAVE
# ============================================================================
st.markdown("## ⚡ Estado Operacional")

STYLE_MAP = {
    "metric-card-fire": "background: linear-gradient(45deg, #FF6F61, #DE483C); color: white; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.1);",
    "metric-card-info": "background: linear-gradient(45deg, #4A90E2, #50E3C2); color: white; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.1);",
    "metric-card-alert": "background: linear-gradient(45deg, #FFD300, #F7B500); color: black; border-radius: 0.5rem; padding: 1rem; box-shadow: 0 4px 8px rgba(0,0,0,0.1);",
}

def generar_html_metrica(clase_css, label, value, delta):
    card_style = STYLE_MAP.get(clase_css, "")
    delta_text_color = "white" if clase_css != "metric-card-alert" else "black"

    html_content = f"""
    <div style="{card_style}">
        <div style="font-size: 1rem; font-weight: 600; opacity: 0.9; margin-bottom: 0.5rem;">{label}</div>
        <div>
            <div style="font-size: 2.5rem; font-weight: 700; line-height: 1.2;">{value}</div>
            <div style="font-size: 1rem; margin-top: 0.2rem;">
                <span style="color: {delta_text_color}; opacity: 0.8;">
                    {delta}
                </span>
            </div>
        </div>
    </div>
    """
    return html_content

col1, col2, col3, col4 = st.columns(4)

with col1:
    html_card1 = generar_html_metrica(
        clase_css="metric-card-fire", 
        label="🔥 Riesgo de Incendio", 
        value=f"{color_riesgo} {nivel_riesgo}", 
        delta=f"{riesgo_calculado}% de riesgo" 
    )
    render_html(html_card1)

with col2:
    delta_temp = "⚠️ SOBRE UMBRAL" if temp_actual > umbral_temperatura else "✓ Normal"
    html_card2 = generar_html_metrica(
        clase_css="metric-card-info", 
        label="🌡️ Temperatura Actual", 
        value=f"{temp_actual}°C", 
        delta=delta_temp
    )
    render_html(html_card2)

with col3:
    delta_hum = "⚠️ BAJO UMBRAL" if humedad_actual < umbral_humedad else "✓ Normal"
    html_card3 = generar_html_metrica(
        clase_css="metric-card-info", 
        label="💧 Humedad Relativa", 
        value=f"{humedad_actual}%", 
        delta=delta_hum
    )
    render_html(html_card3)

with col4:
    html_card4 = generar_html_metrica(
        clase_css="metric-card-alert", 
        label="⚠️ Alertas Activas", 
        value=str(alertas_activas), 
        delta=f"{alertas_activas}/5 umbrales excedidos"  # Cambiar de 4 a 5
    )
    render_html(html_card4)

st.markdown("---")

# ============================================================================
# SISTEMA DE PESTAÑAS PRINCIPAL
# ============================================================================
tab1, tab2, tab3 = st.tabs([
    "🗺️ Mapa Interactivo",
    "🛰️ Análisis Satelital",
    "📈 Índices y Métricas"
])

# ============================================================================
# TAB 1: MAPA INTERACTIVO
# ============================================================================
with tab1:
    st.markdown("### 🗺️ Monitoreo Meteorológico y Focos de Calor")

    col1, col2 = st.columns([3, 1]) 

    with col1:
        coordenada_lat = -46.31050588037077
        coordenada_lon = -73.42610705801674
        nivel_zoom = 10
        
        # --- Diccionario español → inglés ---
        capas_mapa = {
            "Viento": "wind",
            "Temperatura": "temp",
            "Nubes": "clouds",
            "Lluvia": "rain",
            "Presión": "pressure"
        }

        # --- Selector visual en español ---
        capa_es = st.selectbox(
            "Seleccionar capa del mapa (Windy):",
            list(capas_mapa.keys()),
            index=0,
            key="windy_layer",
            help="Elige la información meteorológica a visualizar"
        )

        # --- Convertir selección al valor técnico en inglés ---
        capa_seleccionada = capas_mapa[capa_es]

        iframe, url = generar_mapa_windy(coordenada_lat, coordenada_lon, nivel_zoom, capa_seleccionada)
        render_html(iframe, height=620)

    with col2:
        st.markdown("#### 📍 Detalles de la Zona")

        st.metric(
            label="📍 Latitud",
            value=f"{coordenada_lat:.4f}°",
            delta="Sur"
        )

        st.metric(
            label="📍 Longitud", 
            value=f"{coordenada_lon:.4f}°",
            delta="Oeste"
        )

        st.metric(
            label="🗺️ Capa Activa",
            value=capa_es.upper()
        )

        # Información adicional en expander
        with st.expander("ℹ️ Información de la Región"):
            st.markdown("""
            **Región de Aysén del General Carlos Ibáñez del Campo**
            
            - 🏔️ Patagonia chilena
            - 🌊 Bahía Exploradores: zona costera glaciar
            - 🌲 Rica biodiversidad y ecosistemas únicos
            - ❄️ Clima frío oceánico
            """)


        st.markdown("#### 🔔 Alertas Locales")
        alertas_mostradas = 0
        
        # Alerta de Temperatura
        if temp_actual > umbral_temperatura:
            st.error(f"🌡️ Temperatura sobre {umbral_temperatura}°C (Actual: {temp_actual}°C)")
            alertas_mostradas += 1
        
        # Alerta de Humedad
        if humedad_actual < umbral_humedad:
            st.error(f"💧 Humedad bajo {umbral_humedad}% (Actual: {humedad_actual}%)")
            alertas_mostradas += 1
        
        # Alerta de NDVI
        if ndvi_actual < umbral_ndvi:
            st.error(f"🌿 NDVI bajo {umbral_ndvi:.2f} (Actual: {ndvi_actual:.2f})")
            alertas_mostradas += 1
        
        # Alerta de NDMI
        if ndmi_actual < umbral_ndmi:
            st.error(f"💦 NDMI bajo {umbral_ndmi:.2f} (Actual: {ndmi_actual:.2f})")
            alertas_mostradas += 1
        
        # Alerta de MIRBI
        if mirbi_actual > umbral_mirbi:
            st.error(f"🔥 MIRBI sobre {umbral_mirbi:.2f} (Actual: {mirbi_actual:.2f})")
            alertas_mostradas += 1
        
        # Mensaje si no hay alertas
        if alertas_mostradas == 0:
            st.success("✅ Sin alertas activas")

# ============================================================================
# TAB 2: ANÁLISIS SATELITAL
# ============================================================================
with tab2:
    st.markdown("### 🛰️ Análisis de Imágenes Satelitales Copernicus")

    # Descripción
    st.write("""
    Selecciona una fecha para visualizar los índices satelitales NDVI, NDMI y MIRBI 
    correspondientes a ese período de captura.
    """)

    # Diccionario con las fechas y sus rutas
    fechas_disponibles = {
        "19 de junio de 2023": "images/19-06-2023",
        "9 de febrero de 2024": "images/09-02-2024",
        "25 de diciembre de 2024": "images/25-12-2024"
    }

    # Selector de fecha
    fecha_seleccionada = st.selectbox(
        "Seleccione una fecha de captura:",
        list(fechas_disponibles.keys()),
        index=1  # Por defecto selecciona la segunda opción (9 de febrero de 2024)
    )

    # Obtener la ruta base según la fecha seleccionada
    ruta_base = fechas_disponibles[fecha_seleccionada]

    st.divider()

    # Mostrar las tres imágenes
    st.subheader(f"Imágenes satelitales del {fecha_seleccionada}")

    # Definir las imágenes y sus descripciones
    indices = {
        "NDVI": {
            "nombre": "NDVI (Índice de Vegetación de Diferencia Normalizada)",
            "descripcion": "Mide la salud y densidad de la vegetación"
        },
        "NDMI": {
            "nombre": "NDMI (Índice de Humedad de Diferencia Normalizada)",
            "descripcion": "Evalúa el contenido de humedad en la vegetación"
        },
        "MIRBI": {
            "nombre": "MIRBI (Índice de Brillo Rojo Medio Infrarrojo)",
            "descripcion": "Detecta áreas quemadas y cambios en la superficie"
        }
    }

    # Crear tres columnas para mostrar las imágenes
    col1, col2, col3 = st.columns(3)

    columnas = [col1, col2, col3]
    nombres_archivos = ["NDVI.png", "NDMI.png", "MIRBI.png"]

    # Mostrar cada imagen en su columna correspondiente
    for i, (col, nombre_archivo) in enumerate(zip(columnas, nombres_archivos)):
        indice_nombre = nombre_archivo.replace(".png", "")
        ruta_imagen = os.path.join(ruta_base, nombre_archivo)
        
        with col:
            st.markdown(f"**{indices[indice_nombre]['nombre']}**")
            
            # Verificar si la imagen existe
            if os.path.exists(ruta_imagen):
                try:
                    imagen = Image.open(ruta_imagen)
                    st.image(imagen, use_container_width=True)
                    st.caption(indices[indice_nombre]['descripcion'])
                except Exception as e:
                    st.error(f"Error al cargar la imagen: {str(e)}")
            else:
                st.warning(f"Imagen no encontrada en: {ruta_imagen}")


# ============================================================================
# TAB 3: ÍNDICES Y MÉTRICAS
# ============================================================================
with tab3:
    st.markdown("### 📈 Resumen de Índices de Riesgo Satelital")

    # Función para obtener estado dinámicamente
    def obtener_estado(valor, umbral, invertido=False):
        """
        Determina el estado de un índice comparándolo con su umbral
        invertido=True: valores bajos son malos (NDVI, NDMI)
        invertido=False: valores altos son malos (MIRBI)
        """
        if invertido:  # Para índices donde bajo es malo
            if valor < umbral:
                return '🔥 Crítico'
            elif valor < umbral + 0.15:
                return '⚠️ Alerta'
            else:
                return '✅ Normal'
        else:  # Para índices donde alto es malo
            if valor > umbral + 0.2:
                return '🔥 Crítico'
            elif valor > umbral:
                return '⚠️ Alerta'
            else:
                return '✅ Normal'

    # Tabla de índices con valores dinámicos
    indices_data = {
        'Índice': ['NDVI', 'NDMI', 'MIRBI'],
        'Valor Actual': [ndvi_actual, ndmi_actual, mirbi_actual],
        'Umbral': [umbral_ndvi, umbral_ndmi, umbral_mirbi],
        'Estado': [
            obtener_estado(ndvi_actual, umbral_ndvi, invertido=True),
            obtener_estado(ndmi_actual, umbral_ndmi, invertido=True),
            obtener_estado(mirbi_actual, umbral_mirbi, invertido=False)
        ],
        'Descripción': [
            'Índice de Vegetación Normalizada',
            'Índice de Humedad de la Vegetación',
            'Índice de Brillo Rojo Medio Infrarrojo'
        ]
    }

    df_indices = pd.DataFrame(indices_data)

    st.dataframe(
        df_indices,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor Actual": st.column_config.ProgressColumn(
                "Valor Actual",
                format="%.2f",
                min_value=-1,
                max_value=1,
            ),
            "Umbral": st.column_config.NumberColumn(
                "Umbral Configurado",
                format="%.2f"
            )
        }
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Valores Actuales vs Umbrales")
        
        # Gráfico dinámico que se actualiza con los sliders
        fig = go.Figure()
        
        # Barras con valores actuales
        fig.add_trace(go.Bar(
            name='Valor Actual',
            x=df_indices['Índice'],
            y=df_indices['Valor Actual'],
            marker_color='#B31B1B',
            text=df_indices['Valor Actual'].round(2),
            textposition='outside'
        ))
        
        # Línea de umbrales (dinámicos desde los sliders)
        fig.add_trace(go.Scatter(
            name='Umbral Crítico',
            x=df_indices['Índice'],
            y=df_indices['Umbral'],
            mode='markers+lines',
            marker=dict(size=12, symbol='line-ew', color='#FFD700', line=dict(width=3)),
            line=dict(dash='dash', width=2, color='#FFD700'),
            text=df_indices['Umbral'].round(2),
            textposition='top center'
        ))
        
        fig.update_layout(
            height=400,
            showlegend=True,
            hovermode='x unified',
            margin=dict(t=40, b=20, l=20, r=20),
            yaxis=dict(range=[-0.2, 1.2], title="Valor del Índice")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Distribución de Estados")
        
        # Gráfico de dona dinámico
        estados_count = df_indices['Estado'].value_counts()
        fig = px.pie(
            values=estados_count.values,
            names=estados_count.index,
            hole=0.5,
            color=estados_count.index,
            color_discrete_map={
                '🔥 Crítico': '#B31B1B',
                '⚠️ Alerta': '#F76B1C',
                '✅ Normal': '#00CC96'
            }
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=14
        )
        fig.update_layout(
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")

col_foot1, col_foot2, col_foot3 = st.columns([1, 2, 1])

with col_foot1:
    st.markdown("**🔥 Firebay v1.0**")
    st.caption("Sistema de Monitoreo Inteligente")

with col_foot2:
    st.markdown("<div style='text-align: center;'>📍 <strong>Región de Aysén • Bahía Exploradores, Chile<strong></div>", unsafe_allow_html=True)
    st.caption("<div style='text-align: center;'>Desarrollado para la prevención y protección de ecosistemas forestales 🌲</div>", unsafe_allow_html=True)

with col_foot3:
    st.markdown("<div style='text-align: right;'><strong>📡 Powered by<strong></div>", unsafe_allow_html=True)
    st.caption("<div style='text-align: right;'>Copernicus Sentinel • Streamlit • Python</div>", unsafe_allow_html=True)