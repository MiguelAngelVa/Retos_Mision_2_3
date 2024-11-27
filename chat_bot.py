from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize

# Descarga 'punkt' para tokenización
nltk.download('punkt')

# Ruta al archivo CSV con datos de viento
path = "D:\\Documentos 2\\Universidad_2\\Programming\\MinTIC\\Proyecto Energias Limpias\\Velocidades_viento_prueba.csv"  # Asegúrate de que el archivo CSV tenga la estructura indicada

# Carga el dataset
def load_wind_data():
    try:
        # Carga el dataset, omitiendo líneas problemáticas
        df = pd.read_csv(path, on_bad_lines='skip')
        
        # Selección de columnas del dataset y renombramiento
        wind_data = df[['codigoestacion', 'codigosensor', 'fechaobservacion', 'valorobservado', 
                        'nombreestacion', 'departamento', 'municipio', 'zonahidrografica', 
                        'latitud', 'longitud', 'descripcionsensor', 'unidadmedida']].rename(
            columns={
                'codigoestacion': 'station_code',
                'codigosensor': 'sensor_code',
                'fechaobservacion': 'observation_date',
                'valorobservado': 'observed_value',
                'nombreestacion': 'station_name',
                'departamento': 'department',
                'municipio': 'municipality',
                'zonahidrografica': 'hydrographic_zone',
                'latitud': 'latitude',
                'longitud': 'longitude',
                'descripcionSensor': 'sensor_description',
                'unidadmedida': 'unit_measure'
            }
        )

        # Reemplaza NaN por valores predeterminados para evitar errores de JSON
        wind_data = wind_data.fillna({
            'station_code': '',
            'sensor_code': '',
            'observation_date': '',
            'observed_value': 0,
            'station_name': '',
            'department': '',
            'municipality': '',
            'hydrographic_zone': '',
            'latitude': 0.0,
            'longitude': 0.0,
            'sensor_description': '',
            'unit_measure': ''
        })
        
        # Convierte el DataFrame a una lista de diccionarios
        return wind_data.to_dict(orient="records")

    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return []

# Carga inicial de los datos de viento
wind_data_list = load_wind_data()

# Función para clasificar la velocidad del viento
def classify_wind_speed(value):
    if value < 1.0:
        return 'Mala'
    elif 1.0 <= value <= 2.0:
        return 'Buena'
    else:
        return 'Excelente'

# Crea una instancia de FastAPI
app = FastAPI()
app.title = "Análisis de Viento para Energía Eólica"
app.version = "1.0.0"

# Define una ruta para la API
@app.get('/', tags=['Home'])
def message():
    return HTMLResponse('<h1>¡Bienvenido al análisis de datos de viento para energía eólica!!!</h1>')

@app.get('/wind-data', tags=['Wind Data'])
def get_wind_data():
    if not wind_data_list:
        raise HTTPException(status_code=500, detail="No wind data available.")
    return wind_data_list

@app.get('/wind-data/{station_code}', tags=['Wind Data'])
def get_wind_data_by_station(station_code: int):
    # Convierte station_code a cadena para la comparación
    station_code_int = int(station_code)

    # Filtra los datos por código de estación
    station_data = [item for item in wind_data_list if item['station_code'] == station_code_int]
    if not station_data:
        return {"detail": "Estación no encontrada"}
    return station_data

@app.get('/wind-data/municipality/{municipality}', tags=['Wind Data'])
def get_wind_data_by_municipality(municipality: str):
    # Filtra los datos por municipio
    filtered_data = [item for item in wind_data_list if municipality.lower() in item['municipality'].lower()]
    return filtered_data

@app.get('/wind-data/hydrographic-zone/{zone}', tags=['Wind Data'])
def get_wind_data_by_zone(zone: str):
    # Filtra los datos por zona hidrológica
    filtered_data = [item for item in wind_data_list if zone.lower() in item['hydrographic_zone'].lower()]
    return filtered_data


@app.get('/wind-data/municipality/classification/{municipality}', tags=['Wind Data'])
def classify_wind_by_municipality(municipality: str):
    """
    Clasifica la velocidad del viento para un municipio específico.
    Devuelve 'Mala', 'Buena' o 'Excelente' en función de los datos disponibles.
    """
    # Filtrar los datos para el municipio solicitado
    municipality_data = [item for item in wind_data_list if municipality.lower() in item['municipality'].lower()]
    
    if not municipality_data:
        raise HTTPException(status_code=404, detail=f"No se encontraron datos para el municipio: {municipality}")
    
    # Calcular la clasificación general basada en las velocidades observadas
    classification_count = {
        'Mala': 0,
        'Buena': 0,
        'Excelente': 0
    }
    
    for item in municipality_data:
        wind_speed = item['observed_value']
        classification = classify_wind_speed(wind_speed)
        classification_count[classification] += 1
    
    # Determinar la clasificación predominante
    predominant_classification = max(classification_count, key=classification_count.get)
    
    return {
        "municipality": municipality,
        "classification": predominant_classification,
        "details": classification_count
    }


@app.post('/wind-data', tags=['Wind Data'])
def create_wind_data(station_code: str, sensor_code: str = Body(), observation_date: str = Body(), observed_value: float = Body(), station_name: str = Body(), department: str = Body(), municipality: str = Body(), hydrographic_zone: str = Body(), latitude: float = Body(), longitude: float = Body(), sensor_description: str = Body(), unit_measure: str = Body()):
    new_wind_data = {
        "station_code": station_code,
        "sensor_code": sensor_code,
        "observation_date": observation_date,
        "observed_value": observed_value,
        "station_name": station_name,
        "department": department,
        "municipality": municipality,
        "hydrographic_zone": hydrographic_zone,
        "latitude": latitude,
        "longitude": longitude,
        "sensor_description": sensor_description,
        "unit_measure": unit_measure
    }
    wind_data_list.append(new_wind_data)
    return new_wind_data

@app.put('/wind-data/{station_code}', tags=['Wind Data'])
def update_wind_data(station_code: str , sensor_code: str = Body(), observation_date: str = Body(), observed_value: float = Body(), station_name: str = Body(), department: str = Body(), municipality: str = Body(), hydrographic_zone: str = Body(), latitude: float = Body(), longitude: float = Body(), sensor_description: str = Body(), unit_measure: str = Body()):
    for item in wind_data_list:
        if item['station_code'] == station_code:
            item.update({
                "sensor_code": sensor_code,
                "observation_date": observation_date,
                "observed_value": observed_value,
                "station_name": station_name,
                "department": department,
                "municipality": municipality,
                "hydrographic_zone": hydrographic_zone,
                "latitude": latitude,
                "longitude": longitude,
                "sensor_description": sensor_description,
                "unit_measure": unit_measure
            })
            return item
    return {"Estación no encontrada"}

@app.delete('/wind-data/{station_code}', tags=['Wind Data'])
def delete_wind_data(station_code: str):
    global wind_data_list
    wind_data_list = [item for item in wind_data_list if item['station_code'] != station_code]
    return {"Estación de viento borrada exitosamente"}


#para correr la app: uvicorn main:app --reload
#uvirconr nombreApp:app --reload --port 5000
# http://127.0.0.1:8000/docs
#Commit: Abordamos hasta la sesion 2 Slide 37