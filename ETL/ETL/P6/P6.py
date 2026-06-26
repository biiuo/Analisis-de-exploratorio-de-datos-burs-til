import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# cargamos el dataset
df = pd.read_csv('dataset.csv')

# convertimos la fecha y extraemos el año
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year

# rango diario = diferencia entre maximo y minimo del dia (volatilidad)
df['Daily_Range'] = df['High'] - df['Low']

# creamos la columna de decada para agrupar por epocas
df['Decade_Label'] = ((df['Year'] // 10) * 10).astype(str) + 's'

# cogemos una muestra de 300 dias por decada ya que si no se satura la grafica y sale una cosa que no se se entiende tan bien
np.random.seed(42)
frames = []
for dec in ['1990s', '2000s', '2010s', '2020s']:
    sub = df[df['Decade_Label'] == dec]
    frames.append(sub.sample(min(300, len(sub))))
df_sample = pd.concat(frames).reset_index(drop=True)

# colores para cada decada
palette = {'1990s': "#2993EA", '2000s': "#FF9B04", '2010s': "#4BB34F", '2020s': '#E91E63'}

# creamos una subgrafica por decada 
g = sns.FacetGrid(df_sample, col='Decade_Label',
                  col_order=['1990s', '2000s', '2010s', '2020s'],
                  height=4, aspect=1.1, sharey=False, sharex=False)

def plot_scatter(data, color, **kwargs):
    c = palette.get(data['Decade_Label'].iloc[0], color)
    
    # tamaño del punto proporcional a la volatilidad del dia
    sizes = (data['Daily_Range'] / data['Daily_Range'].max()) * 120 + 10
    plt.scatter(data['Volume'] / 1e6, data['Close'],
                s=sizes, alpha=0.45, color=c, edgecolors='white', linewidths=0.3)
    # linea de tendencia lineal
    z = np.polyfit(data['Volume'] / 1e6, data['Close'], 1)
    p = np.poly1d(z)
    xline = np.linspace((data['Volume'] / 1e6).min(), (data['Volume'] / 1e6).max(), 100)
    plt.plot(xline, p(xline), color='black', linewidth=1.2, linestyle='--', alpha=0.6)

g.map_dataframe(plot_scatter)

# etiquetas y titulos
g.set_axis_labels('Volumen (millones)', 'Precio de cierre (EUR)')
g.set_titles(col_template='Decada: {col_name}')
g.figure.suptitle('BMW AG: Precio de cierre vs Volumen por decada\n(tamano del punto = volatilidad diaria)',
                   fontsize=13, fontweight='bold', y=1.03)
g.figure.text(0.5, -0.02,
              'Linea discontinua = tendencia lineal  |  Cada punto = un dia de cotizacion',
              ha='center', fontsize=9, color='gray')

plt.tight_layout()

# guardamos con alta resolucion (200 dpi)
plt.savefig('grafica.png', dpi=200, bbox_inches='tight')
print('Imagen guardada como grafica.png')
plt.show()

# ---- COMENTARIOS TECNICOS ----
# La grafica relaciona 4 dimensiones: el precio (Y), volumen (X), volatilidad (tamaño punto) y decada (color)
#
#  1990s: precios bajos (15-30 EUR), poco volumen y poca volatilidad, mercado tranquilo
#  2000s: precios suben pero la crisis del 2008 genera puntos grandes (mucha volatilidad)
#  2010s: maximos historicos (100 EUR), tendencia positiva clara entre volumen y precio
#  2020s: el COVID en 2020 provoca puntos enormes, es decir mucho volumen debido a el panico en el mercado y se consigue una tendencia positiva
#   mayor a la de la decada anterior

#
# Esta grafica es bastante util ya q permite ver de un vistazo en q epocas el valor era mas estable
# y en cuales habia mas riesgo, lo que ayudaria a tomar decisiones de inversion ya q asi el cliente o la empresa puede ver como se comporto el
# mercado ante estas situaciones y ver si prefiere tomar menores riesgos asegurando mas su benefico, lo contrario o si se repite de forma parecida
# algunas de estas situaciones (crisis/confinamiento/estabilidad) en el futuro tendria una idea matematicamente aproximada de que podria pasar
