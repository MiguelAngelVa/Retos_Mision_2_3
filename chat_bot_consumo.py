from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
import json

app = FastAPI()

# Constantes de consumo de energía
ELECTRODOMESTICOS = {
    "nevera": 1.2,  # kWh por hora
    "lavadora": 0.5,
    "televisor": 0.1,
    "computador": 0.2,
    "aire_acondicionado": 1.5,
    "microondas": 1.2,
}

PRECIOS_KWH = {
    1: 200,
    2: 300,
    3: 400,
    4: 500,
    5: 600,
    6: 700,
    7: 700,
}

# Variable global para almacenar las respuestas del usuario
usuario_info = {}

# Ruta inicial: Saludo y bienvenida
@app.get("/", response_class=HTMLResponse)
async def inicio():
    return """
    <h1>Bienvenido al Chatbot de Consumo de Energía</h1>
    <p>Por favor, ingresa los datos paso a paso para calcular tu consumo de energía y opciones de ahorro con paneles solares.</p>
    """

# Ruta para iniciar una nueva conversación (resetear los datos)
@app.get("/iniciar")
async def iniciar_chat():
    global usuario_info
    usuario_info = {}  # Resetear datos
    return {"mensaje": "Hola! Empecemos. ¿Cuál es tu nombre?"}

# Ruta para recibir el nombre del usuario
@app.post("/nombre")
async def recibir_nombre(nombre: str):
    global usuario_info
    usuario_info['nombre'] = nombre
    return {
        "mensaje": f"Hola {nombre}! Ahora dime, ¿en qué departamento vives?"
    }

# Ruta para recibir el departamento
@app.post("/departamento")
async def recibir_departamento(departamento: str):
    global usuario_info
    usuario_info['departamento'] = departamento
    return {
        "mensaje": f"Perfecto. Ahora, ¿en qué municipio vives en {departamento}?"
    }

# Ruta para recibir el municipio
@app.post("/municipio")
async def recibir_municipio(municipio: str):
    global usuario_info
    usuario_info['municipio'] = municipio
    return {
        "mensaje": f"Genial, ahora dime, ¿cuántas personas viven en tu casa?"
    }

# Ruta para recibir la cantidad de personas en la casa
@app.post("/personas")
async def recibir_personas(personas: int):
    global usuario_info
    usuario_info['personas'] = personas
    return {
        "mensaje": f"Perfecto, ahora vamos a ver una lista de electrodomésticos comunes. Por favor, selecciona los electrodomésticos que utilizas y las horas diarias de uso."
    }

# Ruta para mostrar la lista de electrodomésticos
@app.get("/electrodomesticos")
async def listar_electrodomesticos():
    electrodomesticos_list = list(ELECTRODOMESTICOS.keys())
    return {
        "mensaje": f"Lista de electrodomésticos disponibles: {', '.join(electrodomesticos_list)}",
        "electrodomesticos": electrodomesticos_list
    }

# Ruta para recibir el uso de electrodomésticos
@app.post("/electrodomesticos")
async def recibir_electrodomesticos(data: dict):
    global usuario_info
    # Guardar uso de electrodomésticos
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Los datos de uso deben ser un diccionario de electrodomésticos y sus horas de uso.")
    
    usuario_info['electrodomesticos'] = data
    return {
        "mensaje": "¡Listo! Ahora, por favor indícame tu estrato social (un número entre 1 y 7)."
    }

# Ruta para recibir el estrato social
@app.post("/estrato")
async def recibir_estrato(estrato: int):
    global usuario_info
    # Validar estrato
    if estrato < 1 or estrato > 7:
        raise HTTPException(status_code=400, detail="El estrato debe estar entre 1 y 7.")
    
    usuario_info['estrato'] = estrato
    # Realizar los cálculos de consumo y costo
    return calcular_consumo()

# Función para calcular el consumo y costos
def calcular_consumo():
    global usuario_info

    # Calcular el consumo de energía
    consumo_diario = sum(
        ELECTRODOMESTICOS[electro] * horas
        for electro, horas in usuario_info['electrodomesticos'].items()
        if electro in ELECTRODOMESTICOS
    )
    
    # Calcular consumos mensuales y anuales
    consumo_mensual = consumo_diario * 30
    consumo_anual = consumo_diario * 365

    # Calcular costos diarios, mensuales y anuales
    costo_kwh = PRECIOS_KWH[usuario_info['estrato']]
    costo_diario = consumo_diario * costo_kwh
    costo_mensual = consumo_mensual * costo_kwh
    costo_anual = consumo_anual * costo_kwh

    # Enviar resultados finales
    return {
        "mensaje": f"¡Gracias por completar el formulario! Aquí están tus resultados:\n"
                   f"Consumo Diario: {consumo_diario:.2f} kWh\n"
                   f"Consumo Mensual: {consumo_mensual:.2f} kWh\n"
                   f"Consumo Anual: {consumo_anual:.2f} kWh\n"
                   f"Costo Diario: ${costo_diario:.2f} COP\n"
                   f"Costo Mensual: ${costo_mensual:.2f} COP\n"
                   f"Costo Anual: ${costo_anual:.2f} COP\n"
                   f"¡Gracias por utilizar nuestro chatbot!"
    }

# Ejecutar la aplicación
# Ejecuta el comando en la terminal:
# uvicorn archivo:app --reload