import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def extract_data(file):
    """Extrae datos del archivo Excel."""
    df = pd.read_excel(file, sheet_name='Sheet1')
    return df

def column_letter_to_index(letter):
    """Convierte una letra de columna (A, B, C, etc.) en un índice numérico."""
    return ord(letter.upper()) - ord('A')

def range_to_indices(column_range):
    """Convierte un rango de letras de columna (A:F) en índices numéricos."""
    start_col, end_col = column_range.split(':')
    start_index = column_letter_to_index(start_col)
    end_index = column_letter_to_index(end_col)
    return list(range(start_index, end_index + 1))

def transform_data(df, start_row, column_range):
    """Transforma los datos según la fila de inicio y el rango de columnas seleccionadas."""
    columns_indices = range_to_indices(column_range)
    df_filtered = df.iloc[start_row:, columns_indices]
    return df_filtered

def load_data(df_filtered, output_file):
    """Carga los datos transformados en un nuevo archivo Excel."""
    df_filtered.to_excel(output_file, index=False)

def etl_process(file, start_row, column_range, output_file):
    """Realiza el proceso ETL completo."""
    try:
        df = extract_data(file)
        df_filtered = transform_data(df, start_row, column_range)
        load_data(df_filtered, output_file)
        st.success(f"Reporte guardado como {output_file}")
        plot_data(file, start_row, column_range)
    except Exception as e:
        st.error(f"Error: {str(e)}")

def plot_data(file, start_row, column_range):
    """Genera gráficos comparativos de Esquizofrenia y Trastorno Bipolar entre países."""
    df = extract_data(file)
    df_filtered = transform_data(df, start_row, column_range)
    
    # Agrupar por país y obtener el promedio más reciente
    df_grouped = df_filtered.groupby('Entity').last().reset_index()
    
    # Calcular el promedio de Esquizofrenia y Trastorno Bipolar
    df_grouped['Promedio'] = (df_grouped['Schizophrenia (%)'] + df_grouped['Bipolar disorder (%)']) / 2
    
    # Ordenar de mayor a menor según el promedio
    df_sorted = df_grouped.sort_values('Promedio', ascending=False).head(10)  # Top 10 países
    
    # Gráfico de barras
    st.subheader("Comparación de Esquizofrenia y Trastorno Bipolar por País")
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(df_sorted))
    width = 0.35
    ax.bar(x, df_sorted['Schizophrenia (%)'], width, label='Esquizofrenia')
    ax.bar([i + width for i in x], df_sorted['Bipolar disorder (%)'], width, label='Trastorno Bipolar')
    ax.set_xlabel('Países')
    ax.set_ylabel('Porcentaje')
    ax.set_title('Comparación de Esquizofrenia y Trastorno Bipolar por País')
    ax.set_xticks([i + width/2 for i in x])
    ax.set_xticklabels(df_sorted['Entity'], rotation=45, ha='right')
    ax.legend()
    st.pyplot(fig)
    
    # Gráfico de torta para el promedio global
    global_schizophrenia = df_grouped['Schizophrenia (%)'].mean()
    global_bipolar = df_grouped['Bipolar disorder (%)'].mean()
    
    st.subheader("Distribución Global Promedio de Esquizofrenia y Trastorno Bipolar")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie([global_schizophrenia, global_bipolar], 
           labels=['Esquizofrenia', 'Trastorno Bipolar'], 
           autopct='%1.1f%%', startangle=90)
    ax.set_title('Distribución Global Promedio de Esquizofrenia y Trastorno Bipolar')
    ax.axis('equal')
    st.pyplot(fig)

# Configuración de la aplicación
st.title('Proceso ETL con Streamlit')
st.write('Sube un archivo Excel para procesar y generar reportes.')

# Subir archivo Excel
uploaded_file = st.file_uploader("Elegir un archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    st.write("Archivo subido correctamente.")
    
    start_row = st.number_input("Fila de Inicio:", min_value=0, value=0, step=1)
    column_range = st.text_input("Rango de Columnas (ejemplo: A:F):", value="A:F")
    
    if st.button("Procesar"):
        etl_process(uploaded_file, start_row, column_range, 'Reportesito.xlsx')
