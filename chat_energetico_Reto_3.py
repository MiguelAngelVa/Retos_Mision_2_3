from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
from pydantic import BaseModel

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

# Contadores de las palabras "ahorro" y "energía"
palabra_count = {"ahorro": 0, "energia": 0}

# Modelo Pydantic para enviar los contadores
class PalabraCount(BaseModel):
    ahorro: int
    energia: int

# Ruta inicial: Interfaz de chat
@app.get("/", response_class=HTMLResponse)
async def inicio():
    return """
    <html>
        <head>
            <style>
                .chat-container {
                    width: 400px;
                    margin: 50px auto;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    font-family: Arial, sans-serif;
                    background-color: #f9f9f9;
                }
                .chat-box {
                    height: 300px;
                    overflow-y: scroll;
                    margin-bottom: 20px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    background-color: #fff;
                    border-radius: 5px;
                }
                .message {
                    margin-bottom: 10px;
                    padding: 5px;
                    border-radius: 5px;
                    background-color: #e1e1e1;
                }
                .user-message {
                    background-color: #c1e1c1;
                    text-align: right;
                }
                .bot-message {
                    background-color: #c1d9e1;
                    text-align: left;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    width: 100%;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div id="chat-box" class="chat-box">
                    <div class="message bot-message">Bienvenidos al chat bot de energía, dime tu nombre:</div>
                </div>
                <input type="text" id="user-input" placeholder="Escribe tu mensaje..."/>
                <button onclick="sendMessage()">Enviar</button>
            </div>

            <script>
                let messages = [];
                
                function addMessage(message, type) {
                    let messageElement = document.createElement('div');
                    messageElement.classList.add('message');
                    messageElement.classList.add(type);
                    messageElement.innerText = message;
                    document.getElementById('chat-box').appendChild(messageElement);
                    document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
                }

                function sendMessage() {
                    let userInput = document.getElementById('user-input').value;
                    if (userInput) {
                        addMessage(userInput, 'user-message');
                        document.getElementById('user-input').value = '';
                        fetch(`/chat/${userInput}`, { method: 'POST' })
                            .then(response => response.json())
                            .then(data => {
                                addMessage(data.mensaje, 'bot-message');
                            });
                    }
                }
            </script>
        </body>
    </html>
    """

# Ruta para recibir y procesar las respuestas del usuario
@app.post("/chat/{mensaje}")
async def chat(mensaje: str):
    global usuario_info, palabra_count
    # Contamos las menciones de las palabras "ahorro" y "energía"
    for palabra in mensaje.lower().split():
        if "ahorro" in palabra:
            palabra_count["ahorro"] += 1
        if "energia" in palabra:
            palabra_count["energia"] += 1
    
    if 'nombre' not in usuario_info:
        usuario_info['nombre'] = mensaje
        return {"mensaje": f"Hola {mensaje}, ahora, cuentanos como te ayudaria en tu hogar la implementación de metodos de generación alternativos de energia?"}
    
    if 'porque?' not in usuario_info:
        usuario_info['porque?'] = mensaje
        return {"mensaje": f"¡Que interesnte razón! ¿En qué departamento vives?"}
    
    if 'departamento' not in usuario_info:
        usuario_info['departamento'] = mensaje
        return {"mensaje": f"Perfecto, ahora, ¿en qué municipio vives en {mensaje}?"}
    
    if 'municipio' not in usuario_info:
        usuario_info['municipio'] = mensaje
        return {"mensaje": f"Genial, ahora, ¿cuántas personas viven en tu casa?"}
    
    if 'personas' not in usuario_info:
        try:
            usuario_info['personas'] = int(mensaje)
            return {
                "mensaje": "Perfecto, a continuación, selecciona las horas de uso diario para los electrodomésticos más comunes:\n" +
                           "\n".join([f"{i + 1}. {electro}" for i, electro in enumerate(ELECTRODOMESTICOS.keys())]) +
                           "\nPor favor, ingresa las horas de uso en el orden indicado, separadas por comas (por ejemplo: 5,2,3,0,4)."
            }
        except ValueError:
            return {"mensaje": "Por favor, ingresa un número válido de personas."}
    
    if 'electrodomesticos' not in usuario_info:
        try:
            # Convertir la respuesta del usuario en una lista de horas
            horas = list(map(float, mensaje.split(",")))
            if len(horas) != len(ELECTRODOMESTICOS):
                return {"mensaje": f"Por favor, ingresa exactamente {len(ELECTRODOMESTICOS)} valores separados por comas."}
            
            # Mapear las horas a los electrodomésticos
            usuario_info['electrodomesticos'] = {
                electro: horas[i]
                for i, electro in enumerate(ELECTRODOMESTICOS.keys())
            }
            return {"mensaje": "¡Listo! Ahora, por favor indícame tu estrato social (un número entre 1 y 7)."}

        except ValueError:
            return {"mensaje": "Por favor, ingresa solo números separados por comas (por ejemplo: 5,2,3,0,4)."}

    if 'estrato' not in usuario_info:
        try:
            estrato = int(mensaje)
            if 1 <= estrato <= 7:
                usuario_info['estrato'] = estrato
                return {"mensaje": "Por último, ¿qué porcentaje consumo quieres ahorrar con paneles solares? (Ingresa un número entre 0 y 100)."}
            else:
                return {"mensaje": "El estrato debe estar entre 1 y 7. Intenta nuevamente."}
        except ValueError:
            return {"mensaje": "Por favor, ingresa un número válido entre 1 y 7."}
    
    if 'panel_solar_porcentaje' not in usuario_info:
        try:
            porcentaje = float(mensaje)
            if 0 <= porcentaje <= 100:
                usuario_info['panel_solar_porcentaje'] = porcentaje / 100  # Convertir a decimal
                return calcular_consumo()
            else:
                return {"mensaje": "El porcentaje debe estar entre 0 y 100. Intenta nuevamente."}
        except ValueError:
            return {"mensaje": "Por favor, ingresa un porcentaje válido como un número entre 0 y 100."}
    
    # Devolvemos los contadores de palabras con el mensaje
    return {"mensaje": "¡Gracias por completar el formulario!", "palabra_count": palabra_count}

# Función para calcular el consumo y costos
def calcular_consumo():
    global usuario_info, palabra_count

    # Calcular el consumo de energía
    consumo_diario = sum(
        ELECTRODOMESTICOS[electro] * horas
        for electro, horas in usuario_info['electrodomesticos'].items()
    ) * usuario_info['personas']
    
    consumo_mensual = consumo_diario * 30
    consumo_anual = consumo_mensual * 12

    # Costos sin ahorro
    costo_diario = consumo_diario * PRECIOS_KWH[usuario_info['estrato']]
    costo_mensual = consumo_mensual * PRECIOS_KWH[usuario_info['estrato']]
    costo_anual = consumo_anual * PRECIOS_KWH[usuario_info['estrato']]

    # Ahorros con paneles solares
    ahorro_diario = costo_diario * usuario_info['panel_solar_porcentaje']
    ahorro_mensual = costo_mensual * usuario_info['panel_solar_porcentaje']
    ahorro_anual = costo_anual * usuario_info['panel_solar_porcentaje']

    # Costos con ahorro
    costo_diario_con_ahorro = costo_diario - ahorro_diario
    costo_mensual_con_ahorro = costo_mensual - ahorro_mensual
    costo_anual_con_ahorro = costo_anual - ahorro_anual

    # Mensaje final con resultados y contadores de palabras
    return {
        "mensaje": f"Resumen del consumo y costos:\n\n"
                   f"Consumo Diario: {consumo_diario:.2f} kWh\n"
                   f"Consumo Mensual: {consumo_mensual:.2f} kWh\n"
                   f"Consumo Anual: {consumo_anual:.2f} kWh\n"
                   f"\nCostos sin ahorro:\n"
                   f"Costo Diario: ${costo_diario:.2f} COP\n"
                   f"Costo Mensual: ${costo_mensual:.2f} COP\n"
                   f"Costo Anual: ${costo_anual:.2f} COP\n"
                   f"\nAhorros por paneles solares:\n"
                   f"Ahorro Diario: ${ahorro_diario * PRECIOS_KWH[usuario_info['estrato']] :.2f} COP\n"
                   f"Ahorro Mensual: ${ahorro_mensual * PRECIOS_KWH[usuario_info['estrato']] :.2f} COP\n"
                   f"Ahorro Anual: ${ahorro_anual * PRECIOS_KWH[usuario_info['estrato']] :.2f} COP\n"
                   f"\nCostos con ahorro:\n"
                   f"Costo Diario: ${costo_diario_con_ahorro:.2f} COP\n"
                   f"Costo Mensual: ${costo_mensual_con_ahorro:.2f} COP\n"
                   f"Costo Anual: ${costo_anual_con_ahorro:.2f} COP\n"
                   f"\nConteo de palabras:\n"
                   f"Ahorro mencionado: {palabra_count['ahorro']} veces\n"
                   f"Energía mencionada: {palabra_count['energia']} veces"
    }
