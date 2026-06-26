import pandas as pd
import numpy as np

def ejercicio_5_bmw():

    #Pt1.Ingesta tecnica:
    print("Iniciando carga y limpieza de datos...")
    try:
        df = pd.read_csv('12_bmw_data.csv')
        df = df.dropna(subset=['Date', 'Adj_Close', 'Volume'])
        
    except FileNotFoundError:
        print("Error: El archivo '12_bmw_data.csv' no se encuentra en el directorio.")
        return

    #Limpieza de Adj_close
    df['Adj_Close'] = df['Adj_Close'].astype(str)
    df['Adj_Close'] = df['Adj_Close'].str.replace('$', '', regex=False)
    df['Adj_Close'] = df['Adj_Close'].str.replace('€', '', regex=False)
    df['Adj_Close'] = df['Adj_Close'].str.replace(',', '', regex=False)
    df['Adj_Close'] = pd.to_numeric(df['Adj_Close'], errors='coerce')

    #Modificar valores nulos con la mediana
    mediana_precio = df['Adj_Close'].median()
    df['Adj_Close'] = df['Adj_Close'].fillna(mediana_precio)

    #Conversion de fechas
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date')

    #Pt2.Ingenieria de caracteristicas:
  
    df['daily_range'] = df['High'] - df['Low'] #Rango diario
    df['daily_return'] = df['Adj_Close'].pct_change() * 100 #Rendimiento diario
    df['year'] = df['Date'].dt.year #Año



    # Pt3.Filtrado cruzado:
    print("Aplicando filtros de volumen de ventas...")

    # Condición 1: Volumen superior a la media
    cond_volumen = df['Volume'] > df['Volume'].mean()
    
    # Condición 2: Volatilidad alta (Días de movimiento significativo)
    cond_volatilidad = df['daily_range'] > df['daily_range'].median()
    
    # Extraemos el subconjunto crítico (df_target) con visibilidad condicionada
    df_target = df[cond_volumen & cond_volatilidad][['Date', 'Adj_Close', 'daily_return']].copy()

    print(f"Registros en df_target que cumplen los criterios lógicos: {len(df_target)}")



    #Pt4.Agregacion y analisis:
    print("Agrupando datos por año...")

    df_resumen_anual = df.groupby('year').agg(
        precio_medio_cierre=('Adj_Close', 'mean'),       
        maximo_historico_anual=('High', 'max'),            
        volumen_total_anual=('Volume', 'sum'),             
        volatilidad_media_anual=('daily_range', 'mean'),   
        num_sesiones=('Date', 'count')                     
    )

    # Ordenamos por volumen total de mayor a menor
    df_resumen_anual = df_resumen_anual.sort_values(by='volumen_total_anual', ascending=False)



    #Pt5.Exportacion de resultados:
    print("\n--- TOP 10 REGISTROS DE ALTA VOLATILIDAD  ---")
    print(df_target.head(10).to_string())

    # Exportamos separando por tabulador
    print("\nExportando reporte anual a CSV...")
    df_resumen_anual.to_csv('reporte_anual_bmw.csv', sep='\t', index=True)
    print("Proceso finalizado con éxito. Archivo: 'reporte_anual_bmw.csv' generado.")


if __name__ == '__main__':
    ejercicio_5_bmw()