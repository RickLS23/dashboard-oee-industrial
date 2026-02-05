import streamlit as st
import pandas as pd
import plotly.express as px

import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard OEE - Maquinaria", layout="wide")

# --- 1. CARGA DE DATOS ---
@st.cache_data # Esto hace que la app sea rápida, no recarga los datos a cada click
def cargar_datos():
    # Obtener la ruta absoluta del directorio del script actual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'datos_produccion.csv')
    
    df = pd.read_csv(data_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

df = cargar_datos()

# --- 2. BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros")
dias_seleccionados = st.sidebar.multiselect(
    "Seleccionar Estado de Máquina:",
    options=df["Estado"].unique(),
    default=df["Estado"].unique()
)

# Filtrar el DataFrame según la selección
df_filtrado = df.query("Estado == @dias_seleccionados")

# --- 3. CÁLCULOS DE OEE (LÓGICA DE NEGOCIO) ---
# Definimos la Capacidad Ideal (ej. la máquina debería hacer 60 piezas/hora)
capacidad_ideal_por_hora = 60 

# A) Disponibilidad: (Tiempo Operando / Tiempo Total Planeado)
total_registros = len(df_filtrado)
tiempo_operando = len(df_filtrado[df_filtrado['Estado'] == 'Operando'])
disponibilidad = tiempo_operando / total_registros if total_registros > 0 else 0

# B) Rendimiento: (Total Piezas / (Tiempo Operando * Capacidad Ideal))
total_piezas = df_filtrado['Piezas_Producidas'].sum()
capacidad_teorica = tiempo_operando * capacidad_ideal_por_hora
rendimiento = total_piezas / capacidad_teorica if capacidad_teorica > 0 else 0

# C) Calidad: ((Piezas Totales - Defectuosas) / Piezas Totales)
total_defectuosas = df_filtrado['Piezas_Defectuosas'].sum()
piezas_buenas = total_piezas - total_defectuosas
calidad = piezas_buenas / total_piezas if total_piezas > 0 else 0

# D) OEE GLOBAL
oee = disponibilidad * rendimiento * calidad

# --- 4. VISUALIZACIÓN (FRONTEND) ---

st.title("🏭 Dashboard de Eficiencia General (OEE)")
st.markdown("Monitorización de producción en tiempo real para la máquina **MAQ-01**.")

# --- SECCIÓN DE TARJETAS (KPIs) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="OEE Global", value=f"{oee:.1%}")
    st.progress(float(oee)) # Barra de progreso visual

with col2:
    st.metric(label="Disponibilidad", value=f"{disponibilidad:.1%}", delta="Tiempo Activo")

with col3:
    st.metric(label="Rendimiento", value=f"{rendimiento:.1%}", delta="Velocidad vs Ideal")

with col4:
    st.metric(label="Calidad", value=f"{calidad:.1%}", delta="- Defectos")

st.markdown("---")

# --- SECCIÓN DE GRÁFICOS ---
col_graf1, col_graf2 = st.columns([2, 1])

with col_graf1:
    st.subheader("Producción por Hora (Tendencia)")
    # Usamos Plotly para un gráfico interactivo
    fig_line = px.line(df_filtrado, x='Timestamp', y='Piezas_Producidas', 
                       title='Piezas Producidas vs Tiempo',
                       markers=True)
    fig_line.update_traces(line_color='#00CC96')
    st.plotly_chart(fig_line, width='stretch')

with col_graf2:
    st.subheader("Distribución de Estados")
    # Gráfico de pastel para ver tiempos muertos
    conteo_estados = df_filtrado['Estado'].value_counts().reset_index()
    conteo_estados.columns = ['Estado', 'Horas']
    
    fig_pie = px.pie(conteo_estados, values='Horas', names='Estado', hole=0.4,
                     color='Estado',
                     color_discrete_map={'Operando':'#00CC96', 'Paro':'#FFA15A', 'Falla':'#EF553B'})
    st.plotly_chart(fig_pie, width='stretch')

# --- TABLA DE DATOS RAW ---
with st.expander("Ver Datos Crudos (Últimos 10 registros)"):
    st.dataframe(df.tail(10))