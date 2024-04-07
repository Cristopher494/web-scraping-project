import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

url = "https://ycharts.com/companies/TSLA/revenues"
response = requests.get(url) # Realiza la solicitud a la url 
time.sleep(10) #Pausa la ejecución del programa para evitar sobrecargar el servidor y para simular un comportamiento más "humano"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"} #Agente de usuario para acceder a la página, debido al error 403
request = requests.get(url, headers=headers) #Los encabezados como parámetros
time.sleep(10)
response = request.text #Extrae el http y lo guarda en formato texto

soup = BeautifulSoup(response, "html.parser") #Se usa BS para analizar el contenido html. Parser es el analizador de html integrado en BS.

tables = soup.find_all("table") #En la sopa se busca una tabla con la clase "table"


data = []   #Se crea una lista vacía

filtered_tables = list(filter(lambda table: "Date" in str(table.th), tables)) # Filtramos las tablas cogiendo únicamente las que contengan un th = Date

for table in filtered_tables:
    for row in table.find_all("tr"): #Se itera sobre cada fila, comenzando desde la segunda.
        col = row.find_all("td") #Se encuentran todas las celdas 'td' en esa fila
        if len(col) == 2:  # asegurarse de que haya exactamente 2 celdas por fila
            date = col[0].text.strip()
            clean_data = col[1].text.strip().replace("$", "").replace(",", "")
            data.append({"Date": date, "Value": clean_data})

# # Crear un DataFrame de pandas con los datos extraídos
df = pd.DataFrame(data)

#Función para quitar la B y M de los valores y dejarlos numéricos
def convert_to_numeric(value):
    if 'B' in value:
        return float(value.replace('B', '')) * 1e9
    elif 'M' in value:
        return float(value.replace('M', '')) * 1e6
    else:
        return float(value)

# Aplicar la función a la columna "Value"
df["Value"] = df["Value"].apply(convert_to_numeric)

#Cambiar el formato de fecha a numérico
df["Date"] = pd.to_datetime(df["Date"])
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

#CONEXIÓN SQL
conn = sqlite3.connect('datos_tesla.db')

cursor = conn.cursor()
cursor.execute("""CREATE TABLE tesla_evolution (Date, Value)""")

tesla_tuples = list(df.to_records(index = False))

cursor.executemany("INSERT INTO tesla_evolution VALUES (?,?)", tesla_tuples)
conn.commit()
conn.close()


#VISUALIZACIÓN DE LOS RESULTADOS   
fig, axis = plt.subplots(figsize = (10, 5))

#Gráfico de líneas
df["Date"] = pd.to_datetime(df["Date"])
sns.lineplot(df, x = "Date", y = "Value")
axis.set_title('Tesla evolution')
plt.tight_layout()
plt.show()

#Gráfico de barras
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df_yearly = df.groupby(df['Date'].dt.year)['Value'].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(data=df_yearly, x='Date', y='Value', ax=ax)
ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.set_title('Tesla evolution')
plt.show()

fig, axis = plt.subplots(figsize = (10, 5))

#Gráfico de dispersión
df["Date"] = pd.to_datetime(df["Date"])
sns.scatterplot(df, x = "Date", y = "Value")
axis.set_title('Tesla evolution')
plt.tight_layout()
plt.show()