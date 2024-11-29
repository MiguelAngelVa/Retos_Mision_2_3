from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Ruta al archivo CSV
path = "D:\\Documentos 2\\Universidad_2\\Programming\\MinTIC\\Proyecto Energias Limpias\\Velocidades_viento_prueba.csv"

# Función para cargar y limpiar los datos
def load_wind_data():
    try:
        # Cargar datos
        df = pd.read_csv(path, on_bad_lines="skip")
        
        # Asegurarse de que 'valorobservado' sea de tipo numérico
        df['valorobservado'] = pd.to_numeric(df['valorobservado'], errors='coerce')
        
        # Eliminar filas con valores NaN
        df = df.dropna(subset=['valorobservado'])
        
        # Renombrar columnas
        df = df.rename(columns={
            'valorobservado': 'observed_value',
            'municipio': 'municipality'
        })
        
        # Agregar una columna de clasificación
        df['classification'] = df['observed_value'].apply(classify_wind_speed)
        return df
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Función para clasificar velocidades del viento
def classify_wind_speed(value):
    if value < 1.0:
        return 'Mala'
    elif 1.0 <= value <= 2.0:
        return 'Buena'
    else:
        return 'Excelente'

# Entrenar un modelo Naive Bayes
def train_naive_bayes_model(df):
    try:
        X = df[['observed_value']].values  # Características (velocidad del viento)
        y = df['classification'].apply(lambda x: {'Mala': 0, 'Buena': 1, 'Excelente': 2}[x]).values  # Clases codificadas
        
        # Dividir los datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar el modelo
        model = GaussianNB()
        model.fit(X_train, y_train)
        
        # Evaluar el modelo
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Precisión del modelo: {accuracy:.2f}")
        
        return model
    except Exception as e:
        print(f"Error al entrenar el modelo: {e}")
        return None

# Cargar los datos y entrenar el modelo
wind_data = load_wind_data()
naive_bayes_model = train_naive_bayes_model(wind_data)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Clasificador de Velocidades de Viento",
    version="1.0.0",
    description="API para clasificar el potencial de implementación de proyectos eólicos."
)

@app.get("/", tags=["Home"])
def home():
    return HTMLResponse("<h1>Bienvenido a la API de Clasificación de Viento para Proyectos Eólicos</h1>")

@app.get("/wind-data/municipality/classification/{municipality}", tags=["Classification"])
def classify_wind_for_municipality(municipality: str):
    """
    Clasifica el potencial eólico de un municipio basado en los datos observados.
    """
    if wind_data.empty:
        raise HTTPException(status_code=500, detail="Los datos no están disponibles.")
    
    # Filtrar datos por municipio
    municipality_data = wind_data[wind_data['municipality'].str.lower() == municipality.lower()]
    
    if municipality_data.empty:
        raise HTTPException(status_code=404, detail=f"No se encontraron datos para el municipio: {municipality}")
    
    # Calcular el promedio de velocidades observadas
    avg_speed = municipality_data['observed_value'].mean()
    
    # Usar el modelo para predecir la clasificación
    prediction = naive_bayes_model.predict([[avg_speed]])[0]
    classification = {0: 'Mala', 1: 'Buena', 2: 'Excelente'}[prediction]
    
    return {
        "municipality": municipality,
        "average_speed": avg_speed,
        "classification": classification
    }

#para correr la app: uvicorn main:app --reload
#uvirconr nombreApp:app --reload --port 5000
# http://127.0.0.1:8000/docs
#Commit: Abordamos hasta la sesion 2 Slide 37

