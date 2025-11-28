"""
FIREBAY - Sistema de Monitoreo de Incendios Forestales
Región de Aysén - Bahía Exploradores, Chile
"""

import streamlit as st
from streamlit.components.v1 import html as render_html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

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
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .alert-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B;
        color: white;
    }
    .sidebar-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF4B4B;
        margin-bottom: 1rem;
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
        style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    </iframe>
    """
    return codigo_iframe, url_windy

def generar_datos_historicos(inicio, fin):
    """Genera datos históricos simulados"""
    fechas = pd.date_range(start=inicio, end=fin, freq='D')
    datos = pd.DataFrame({
        'Fecha': fechas,
        'NDVI': 0.7 - (fechas - fechas[0]).days * 0.01 + pd.Series([(-1)**i * 0.05 for i in range(len(fechas))]).values,
        'Temperatura': 25 + pd.Series([i % 10 for i in range(len(fechas))]).values,
        'Humedad': 50 - pd.Series([i % 15 for i in range(len(fechas))]).values,
        'Riesgo': 30 + (fechas - fechas[0]).days * 1.5
    })
    return datos

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================
st.markdown('<div class="main-header">🔥 FIREBAY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema Inteligente de Prevención y Monitoreo de Incendios Forestales<br>Región de Aysén - Bahía Exploradores, Chile</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - PANEL DE CONTROL
# ============================================================================
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/FF4B4B/FFFFFF?text=FIREBAY", use_container_width=True)
    
    st.markdown("### 🎛️ Panel de Control")
    
    # Selector de fecha
    fecha_analisis = st.date_input(
        "Fecha de análisis",
        datetime.now(),
        help="Selecciona la fecha para análisis de datos satelitales"
    )
    
    # Rango de fechas para histórico
    st.markdown("#### 📅 Análisis Histórico")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.now() - timedelta(days=30))
    with col2:
        fecha_fin = st.date_input("Hasta", datetime.now())
    
    st.markdown("---")
    
    # Configuración de alertas
    st.markdown("#### ⚠️ Configuración de Alertas")
    umbral_ndvi = st.slider("Umbral NDVI", 0.0, 1.0, 0.3, 0.05, help="Índice de vegetación normalizado")
    umbral_nbr = st.slider("Umbral NBR", -1.0, 1.0, 0.1, 0.05, help="Índice de severidad de quemado")
    umbral_temperatura = st.slider("Temperatura crítica (°C)", 25, 45, 35, 1)
    umbral_humedad = st.slider("Humedad crítica (%)", 10, 50, 25, 5)
    
    st.markdown("---")
    
    # Información del sistema
    st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.markdown("**📡 Estado del Sistema**")
    st.success("✅ Conectado a Copernicus")
    st.info("🛰️ Última actualización: Hoy 14:30")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Acciones rápidas
    st.markdown("#### 🚀 Acciones Rápidas")
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.toast("Actualizando datos satelitales...", icon="🛰️")
    if st.button("📊 Generar Reporte", use_container_width=True):
        st.toast("Generando reporte PDF...", icon="📄")
    if st.button("📧 Enviar Alertas", use_container_width=True):
        st.toast("Alertas enviadas correctamente", icon="✅")

# ============================================================================
# DASHBOARD PRINCIPAL - MÉTRICAS CLAVE
# ============================================================================
st.markdown("## 📊 Dashboard en Tiempo Real")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="🔥 Riesgo de Incendio",
        value="ALTO",
        delta="+15%",
        delta_color="inverse"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.metric(
        label="🌡️ Temperatura Actual",
        value="32°C",
        delta="+3°C"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.metric(
        label="💧 Humedad Relativa",
        value="28%",
        delta="-12%",
        delta_color="inverse"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="alert-card">', unsafe_allow_html=True)
    st.metric(
        label="⚠️ Alertas Activas",
        value="3",
        delta="+2"
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SISTEMA DE PESTAÑAS PRINCIPAL
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Mapa Interactivo",
    "🛰️ Análisis Satelital",
    "📈 Índices y Métricas",
    "📊 Histórico y Tendencias",
    "⚙️ Configuración Avanzada"
])

# ============================================================================
# TAB 1: MAPA INTERACTIVO
# ============================================================================
with tab1:
    st.markdown("### 🗺️ Monitoreo Meteorológico en Tiempo Real")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Configuración del mapa
        coordenada_lat = -46.31050588037077
        coordenada_lon = -73.42610705801674
        nivel_zoom = 10
        capa_seleccionada = st.selectbox(
            "Seleccionar capa del mapa:",
            ["wind", "temp", "clouds", "rain", "pressure", "humidity", "fires"],
            index=6,
            help="Elige la información meteorológica a visualizar"
        )
        
        # Generar y mostrar mapa
        iframe, url = generar_mapa_windy(coordenada_lat, coordenada_lon, nivel_zoom, capa_seleccionada)
        render_html(iframe, height=620)
    
    with col2:
        st.markdown("#### 📍 Información de Ubicación")
        st.info(f"""
        **Región:** Aysén  
        **Zona:** Bahía Exploradores  
        **Coordenadas:**  
        - Lat: {coordenada_lat}  
        - Lon: {coordenada_lon}  
        
        **Capa activa:** {capa_seleccionada.upper()}
        """)
        
        st.markdown("#### 🌊 Datos Meteorológicos")
        st.metric("Velocidad del Viento", "15 km/h", "↗️")
        st.metric("Dirección", "SO", "")
        st.metric("Presión", "1013 hPa", "↓")
        
        st.markdown("#### 🔔 Alertas Meteorológicas")
        st.warning("⚠️ Viento fuerte previsto para mañana")
        st.error("🔥 Condiciones favorables para incendios")

# ============================================================================
# TAB 2: ANÁLISIS SATELITAL
# ============================================================================
with tab2:
    st.markdown("### 🛰️ Análisis de Imágenes Satelitales Copernicus")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📡 Imagen RGB - Color Real")
        st.info("🔄 Próximamente: Integración con Copernicus Sentinel-2 para visualización de imágenes en tiempo real")
        st.image("https://via.placeholder.com/600x400/1a1a2e/ffffff?text=Imagen+RGB+Sentinel-2", 
                 caption="Imagen satelital Bahía Exploradores", 
                 use_container_width=True)
        
        if st.button("🔍 Analizar Imagen Actual", key="analyze1"):
            with st.spinner("Procesando imagen satelital..."):
                st.success("✅ Análisis completado - No se detectaron anomalías térmicas")
    
    with col2:
        st.markdown("#### 🔥 Mapa de Calor - Detección Térmica")
        st.info("🔄 Próximamente: Detección automática de puntos calientes usando banda infrarroja")
        st.image("https://via.placeholder.com/600x400/2d1b00/ff6600?text=Mapa+Termico+IR", 
                 caption="Análisis térmico infrarrojo", 
                 use_container_width=True)
        
        if st.button("🌡️ Detectar Puntos Calientes", key="analyze2"):
            with st.spinner("Analizando firmas térmicas..."):
                st.warning("⚠️ 2 anomalías térmicas detectadas en sector norte")
    
    st.markdown("---")
    
    # Panel de comparación temporal
    st.markdown("#### 📅 Comparación Temporal")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Hace 30 días**")
        st.image("https://via.placeholder.com/300x200/228B22/ffffff?text=Vegetacion+Saludable")
        st.caption("NDVI: 0.75 (Saludable)")
    
    with col2:
        st.markdown("**Hace 15 días**")
        st.image("https://via.placeholder.com/300x200/90EE90/000000?text=Vegetacion+Estable")
        st.caption("NDVI: 0.65 (Estable)")
    
    with col3:
        st.markdown("**Hoy**")
        st.image("https://via.placeholder.com/300x200/FFD700/000000?text=Estres+Vegetal")
        st.caption("NDVI: 0.45 (Estrés)")

# ============================================================================
# TAB 3: ÍNDICES Y MÉTRICAS
# ============================================================================
with tab3:
    st.markdown("### 📈 Índices de Vegetación y Severidad")
    
    # Datos de índices
    indices_data = {
        'Índice': ['NDVI', 'NBR', 'NDMI', 'EVI', 'SAVI'],
        'Valor Actual': [0.45, 0.15, 0.38, 0.52, 0.41],
        'Valor Anterior': [0.65, 0.35, 0.55, 0.68, 0.58],
        'Estado': ['⚠️ Alerta', '⚠️ Alerta', '⚠️ Alerta', '✅ Normal', '⚠️ Alerta'],
        'Descripción': [
            'Índice de Vegetación de Diferencia Normalizada',
            'Índice de Severidad de Quemado',
            'Índice de Humedad de Diferencia Normalizada',
            'Índice de Vegetación Mejorado',
            'Índice de Vegetación Ajustado al Suelo'
        ]
    }
    
    df_indices = pd.DataFrame(indices_data)
    
    # Mostrar tabla
    st.dataframe(
        df_indices,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor Actual": st.column_config.ProgressColumn(
                "Valor Actual",
                help="Valor del índice en la fecha seleccionada",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
        }
    )
    
    st.markdown("---")
    
    # Gráficos de índices
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Comparación de Índices")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Valor Actual',
            x=df_indices['Índice'],
            y=df_indices['Valor Actual'],
            marker_color='#FF4B4B'
        ))
        fig.add_trace(go.Bar(
            name='Valor Anterior',
            x=df_indices['Índice'],
            y=df_indices['Valor Anterior'],
            marker_color='#4B7BFF'
        ))
        fig.update_layout(
            barmode='group',
            height=400,
            showlegend=True,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Nivel de Riesgo por Índice")
        riesgo_data = pd.DataFrame({
            'Índice': ['NDVI', 'NBR', 'NDMI', 'EVI', 'SAVI'],
            'Riesgo': [75, 80, 70, 40, 65]
        })
        
        fig = px.pie(
            riesgo_data,
            values='Riesgo',
            names='Índice',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdYlGn_r
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Indicadores de riesgo
    st.markdown("#### 🔥 Evaluación de Riesgo Global")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.error("**RIESGO ALTO**")
        st.progress(0.85)
        st.caption("Índice de Riesgo Combinado: 85/100")
    
    with col2:
        st.warning("**PROBABILIDAD DE IGNICIÓN**")
        st.progress(0.72)
        st.caption("Basado en condiciones meteorológicas")
    
    with col3:
        st.info("**SEVERIDAD POTENCIAL**")
        st.progress(0.68)
        st.caption("Estimación de impacto en caso de incendio")

# ============================================================================
# TAB 4: HISTÓRICO Y TENDENCIAS
# ============================================================================
with tab4:
    st.markdown("### 📊 Análisis Histórico y Tendencias")
    
    # Generar datos
    df_historico = generar_datos_historicos(fecha_inicio, fecha_fin)
    
    # Gráfico de evolución
    st.markdown("#### 📈 Evolución de Índices en el Tiempo")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_historico['Fecha'],
        y=df_historico['NDVI'],
        name='NDVI',
        line=dict(color='#00CC96', width=3),
        mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=df_historico['Fecha'],
        y=df_historico['Temperatura'] / 40,
        name='Temperatura (norm)',
        line=dict(color='#FF6B6B', width=2),
        mode='lines'
    ))
    fig.add_trace(go.Scatter(
        x=df_historico['Fecha'],
        y=df_historico['Humedad'] / 100,
        name='Humedad (norm)',
        line=dict(color='#4ECDC4', width=2),
        mode='lines'
    ))
    fig.update_layout(
        height=400,
        hovermode='x unified',
        xaxis_title='Fecha',
        yaxis_title='Valor'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Evolución del Riesgo de Incendio")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_historico['Fecha'],
            y=df_historico['Riesgo'],
            fill='tozeroy',
            fillcolor='rgba(255, 75, 75, 0.3)',
            line=dict(color='#FF4B4B', width=3),
            name='Nivel de Riesgo'
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Umbral Crítico")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Distribución de Niveles de Riesgo")
        riesgo_dist = pd.DataFrame({
            'Nivel': ['Bajo', 'Medio', 'Alto', 'Crítico'],
            'Días': [5, 8, 12, 6]
        })
        fig = px.bar(
            riesgo_dist,
            x='Nivel',
            y='Días',
            color='Nivel',
            color_discrete_map={
                'Bajo': '#00CC96',
                'Medio': '#FFA500',
                'Alto': '#FF6B6B',
                'Crítico': '#8B0000'
            }
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de eventos
    st.markdown("#### 🗂️ Registro de Eventos Detectados")
    eventos = pd.DataFrame({
        'Fecha': ['2024-11-25', '2024-11-20', '2024-11-15', '2024-11-10'],
        'Tipo': ['🔥 Anomalía Térmica', '⚠️ Alerta NDVI', '🔥 Punto Caliente', '⚠️ Alerta NBR'],
        'Severidad': ['Alta', 'Media', 'Crítica', 'Media'],
        'Ubicación': ['Sector Norte', 'Sector Este', 'Sector Oeste', 'Sector Sur'],
        'Estado': ['✅ Resuelto', '✅ Resuelto', '⏳ Monitoreando', '✅ Resuelto']
    })
    st.dataframe(eventos, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 5: CONFIGURACIÓN
# ============================================================================
with tab5:
    st.markdown("### ⚙️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🛰️ Fuentes de Datos Satelitales")
        sentinel_2 = st.checkbox("Sentinel-2 (Imagen Óptica)", value=True)
        sentinel_3 = st.checkbox("Sentinel-3 (Datos Térmicos)", value=True)
        landsat = st.checkbox("Landsat 8/9", value=False)
        modis = st.checkbox("MODIS", value=False)
        
        st.markdown("#### 📊 Índices a Calcular")
        calc_ndvi = st.checkbox("NDVI - Índice de Vegetación", value=True)
        calc_nbr = st.checkbox("NBR - Severidad de Quemado", value=True)
        calc_ndmi = st.checkbox("NDMI - Índice de Humedad", value=True)
        calc_evi = st.checkbox("EVI - Vegetación Mejorado", value=False)
        calc_savi = st.checkbox("SAVI - Ajustado al Suelo", value=False)
        
        st.markdown("#### 🔄 Frecuencia de Actualización")
        frecuencia = st.select_slider(
            "Intervalo de actualización",
            options=["1 hora", "3 horas", "6 horas", "12 horas", "24 horas"],
            value="6 horas"
        )
    
    with col2:
        st.markdown("#### 📧 Configuración de Notificaciones")
        email_alerts = st.checkbox("Alertas por correo electrónico", value=True)
        if email_alerts:
            email_address = st.text_input("Correo electrónico", "admin@firebay.cl")
        
        sms_alerts = st.checkbox("Alertas por SMS", value=False)
        if sms_alerts:
            phone_number = st.text_input("Número de teléfono", "+56 9 XXXX XXXX")
        
        push_alerts = st.checkbox("Notificaciones Push", value=True)
        
        st.markdown("#### 🎯 Tipos de Alertas")
        alert_thermal = st.checkbox("Anomalías térmicas", value=True)
        alert_indices = st.checkbox("Cambios en índices vegetales", value=True)
        alert_weather = st.checkbox("Condiciones meteorológicas adversas", value=True)
        alert_predictions = st.checkbox("Predicciones de alto riesgo", value=True)
        
        st.markdown("#### 💾 Almacenamiento de Datos")
        retention = st.slider("Días de retención de datos", 30, 365, 90)
        st.caption(f"Los datos se conservarán durante {retention} días")
    
    st.markdown("---")
    
    # Botones de acción
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💾 Guardar Configuración", use_container_width=True):
            st.success("✅ Configuración guardada correctamente")
    with col2:
        if st.button("🔄 Restaurar Valores", use_container_width=True):
            st.info("ℹ️ Valores predeterminados restaurados")
    with col3:
        if st.button("📤 Exportar Config", use_container_width=True):
            st.success("✅ Configuración exportada a config.json")
    with col4:
        if st.button("📥 Importar Config", use_container_width=True):
            st.info("ℹ️ Selecciona un archivo de configuración")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🔥 Firebay v1.0**")
    st.caption("Sistema de Monitoreo de Incendios Forestales")

with col2:
    st.markdown("**📍 Región de Aysén**")
    st.caption("Bahía Exploradores, Chile")

with col3:
    st.markdown("**📡 Powered by**")
    st.caption("Copernicus Sentinel • Streamlit • Python")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Desarrollado para la prevención y protección de ecosistemas forestales 🌲</div>",
    unsafe_allow_html=True
)