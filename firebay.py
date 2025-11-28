import streamlit as st
from streamlit.components.v1 import html as render_html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

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

def calcular_nivel_riesgo(temp, humedad, ndvi, nbr, temp_threshold, hum_threshold, ndvi_threshold, nbr_threshold):
    """Calcula el nivel de riesgo basado en los umbrales"""
    puntos = 0

    # Temperatura
    if temp > temp_threshold:
        puntos += 25
    elif temp > temp_threshold - 5:
        puntos += 15

    # Humedad (invertido: baja humedad = más riesgo)
    if humedad < hum_threshold:
        puntos += 25
    elif humedad < hum_threshold + 10:
        puntos += 15

    # NDVI (bajo = más riesgo)
    if ndvi < ndvi_threshold:
        puntos += 25
    elif ndvi < ndvi_threshold + 0.15:
        puntos += 15

    # NBR (bajo = más riesgo)
    if nbr < nbr_threshold:
        puntos += 25
    elif nbr < nbr_threshold + 0.1:
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
    st.image("https://via.placeholder.com/300x100/B31B1B/FFFFFF?text=FIREBAY+LOGO", use_container_width=True)

    st.markdown("---")

    st.markdown("### 🎛️ Controles Principales")

    st.markdown("#### ⚠️ Umbrales de Alerta")
    umbral_ndvi = st.slider("Umbral NDVI crítico", 0.0, 1.0, 0.3, 0.05, help="Índice de vegetación normalizado (valores bajos = alerta)")
    umbral_nbr = st.slider("Umbral NBR crítico", -1.0, 1.0, 0.1, 0.05, help="Índice de severidad de quemado (valores altos = alerta de quema)")

    col_temp, col_hum = st.columns(2)
    with col_temp:
        umbral_temperatura = st.slider("Temp. Crítica (°C)", 25, 45, 35, 1)
    with col_hum:
        umbral_humedad = st.slider("Hum. Crítica (%)", 10, 50, 25, 5)

    st.markdown("---")

    st.markdown("### 🚀 Acciones Rápidas")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
    with col_btn2:
        if st.button("📧 Alertas", use_container_width=True):
            st.toast("Alertas enviadas", icon="✅")

    if st.button("📊 Generar Reporte", use_container_width=True, type="secondary"):
        st.toast("Generando reporte...", icon="📄")

# ============================================================================
# CÁLCULOS DINÁMICOS BASADOS EN UMBRALES
# ============================================================================

# Valores actuales simulados
temp_actual = 32
humedad_actual = 28
ndvi_actual = 0.45
nbr_actual = 0.15

# Calcular riesgo dinámicamente
riesgo_calculado = calcular_nivel_riesgo(
    temp_actual, humedad_actual, ndvi_actual, nbr_actual,
    umbral_temperatura, umbral_humedad, umbral_ndvi, umbral_nbr
)

# Determinar nivel de riesgo
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

# Calcular alertas activas
alertas_activas = 0
if temp_actual > umbral_temperatura:
    alertas_activas += 1
if humedad_actual < umbral_humedad:
    alertas_activas += 1
if ndvi_actual < umbral_ndvi:
    alertas_activas += 1
if nbr_actual < umbral_nbr:
    alertas_activas += 1

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
        delta=f"{alertas_activas}/4 umbrales excedidos"
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
        
        capa_seleccionada = st.selectbox(
            "Seleccionar capa del mapa (Windy):",
            ["wind", "temp", "clouds", "rain", "pressure"], 
            index=0,
            key="windy_layer",
            help="Elige la información meteorológica a visualizar"
        )

        iframe, url = generar_mapa_windy(coordenada_lat, coordenada_lon, nivel_zoom, capa_seleccionada)
        render_html(iframe, height=620)

    with col2:
        st.markdown("#### 📍 Detalles de la Zona")
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px;">
            <strong>Región:<strong> Aysén 🇨🇱 <br>
            <strong>Zona:<strong> Bahía Exploradores <br><br>
            <strong>Coordenadas:<strong> <br>
            - Lat: {coordenada_lat:.4f} <br>
            - Lon: {coordenada_lon:.4f} <br>
            <strong>Capa Activa:<strong> {capa_seleccionada.upper()}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🌬️ Datos Meteorológicos")
        st.metric("Velocidad del Viento", "15 km/h", "↗️")
        st.metric("Dirección", "SO", "")
        st.metric("Presión Atmosférica", "1013 hPa", "↓")

        st.markdown("#### 🔔 Alertas Locales")
        if temp_actual > umbral_temperatura:
            st.error(f"🌡️ Temperatura sobre {umbral_temperatura}°C")
        if humedad_actual < umbral_humedad:
            st.error(f"💧 Humedad bajo {umbral_humedad}%")

# ============================================================================
# TAB 2: ANÁLISIS SATELITAL
# ============================================================================
with tab2:
    st.markdown("### 🛰️ Análisis de Imágenes Satelitales Copernicus")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📸 Imagen RGB - Color Real")
        st.image("https://via.placeholder.com/600x400/1a1a2e/ffffff?text=Imagen+RGB+Sentinel-2", 
                  caption=f"Sentinel-2", 
                  use_container_width=True)

        if ndvi_actual < umbral_ndvi:
            st.error(f"⚠️ NDVI actual ({ndvi_actual:.2f}) está bajo el umbral crítico ({umbral_ndvi:.2f})")
        else:
            st.success(f"✅ NDVI actual ({ndvi_actual:.2f}) dentro de rangos normales")

    with col2:
        st.markdown("#### 🔥 Mapa de Calor - Detección Térmica")
        st.image("https://via.placeholder.com/600x400/2d1b00/ff6600?text=Mapa+Termico+IR", 
                  caption=f"Análisis Térmico", 
                  use_container_width=True)

        if nbr_actual < umbral_nbr:
            st.error(f"⚠️ NBR actual ({nbr_actual:.2f}) indica condiciones críticas")
        else:
            st.info(f"NBR actual: {nbr_actual:.2f}")

# ============================================================================
# TAB 3: ÍNDICES Y MÉTRICAS
# ============================================================================
with tab3:
    st.markdown("### 📈 Resumen de Índices de Riesgo Satelital")

    # Generar estados dinámicamente
    def obtener_estado(valor, umbral, invertido=False):
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

    indices_data = {
        'Índice': ['NDVI', 'NBR', 'NDMI', 'EVI', 'SAVI'],
        'Valor Actual': [ndvi_actual, nbr_actual, 0.38, 0.52, 0.41],
        'Umbral': [umbral_ndvi, umbral_nbr, 0.30, 0.40, 0.35],
        'Estado': [
            obtener_estado(ndvi_actual, umbral_ndvi, invertido=True),
            obtener_estado(nbr_actual, umbral_nbr, invertido=True),
            obtener_estado(0.38, 0.30, invertido=True),
            '✅ Normal',
            '⚠️ Alerta'
        ],
        'Descripción': [
            'Índice de Vegetación Normalizada (Estrés)',
            'Índice de Severidad de Quemado',
            'Índice de Humedad Normalizada',
            'Índice de Vegetación Mejorado',
            'Índice Ajustado al Suelo'
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
                min_value=0,
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
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Valor Actual',
            x=df_indices['Índice'],
            y=df_indices['Valor Actual'],
            marker_color='#B31B1B'
        ))
        fig.add_trace(go.Scatter(
            name='Umbral Crítico',
            x=df_indices['Índice'],
            y=df_indices['Umbral'],
            mode='markers+lines',
            marker=dict(size=12, symbol='line-ew', color='#FFD700', line=dict(width=3)),
            line=dict(dash='dash', width=2, color='#FFD700')
        ))
        fig.update_layout(
            height=400,
            showlegend=True,
            hovermode='x unified',
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Distribución de Estados")
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
        fig.update_layout(
            height=400,
            margin=dict(t=20, b=20, l=20, r=20)
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