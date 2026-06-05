import requests
import os
import json
import re
from datetime import datetime
from openai import OpenAI
from grok_client import GrokClient
from dotenv import load_dotenv

FS_CLIENT_ID = "0c736cfe1eb640b9828ce01ce5b03ce0"
FS_CLIENT_SECRET = "d4d3b2bf2cc74b65bb73cb0112fc5d2f"

def obtener_datos_fatsecret(alimento: str) -> str:
    #Se conecta a FatSecret, busca el alimento y devuelve la información en texto sin formato.
    token_url = "https://oauth.fatsecret.com/connect/token"
    
    try:
        response = requests.post(
            token_url,
            data={"grant_type": "client_credentials", "scope": "basic"},
            auth=(FS_CLIENT_ID, FS_CLIENT_SECRET)
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
    except Exception as e:
        return f"Error: Could not retrieve FatSecret access token. Details: {e}"
    
    if not access_token:
        return "Error: Access token missing from FatSecret response."

    # Buscar el alimento en la base de datos
    search_url = "https://platform.fatsecret.com/rest/server.api"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "method": "foods.search", 
        "search_expression": alimento, 
        "format": "json"
    }
    
    try:
        food_response = requests.get(search_url, params=params, headers=headers)
        food_response.raise_for_status()
        foods = food_response.json()
    except Exception as e:
        return f"Error: Search request to FatSecret failed. Details: {e}"

    if "error" in foods:
        return f"API Error: {foods['error'].get('message', 'Unknown FatSecret Error')}"

    if "foods" in foods and "food" in foods["foods"]:
        resultados = foods["foods"]["food"]
        
        if isinstance(resultados, dict):
            resultados = [resultados]

        texto_api = ""
        # Enviando los 5 mejores resultados para que la IA tenga mejores datos para promediar
        for food in resultados[:5]:
            texto_api += f"- Name: {food.get('food_name')}\n"
            texto_api += f"  Nutritional Info: {food.get('food_description')}\n"
        
        return texto_api
    else:
        return "No results found for that food in the database."

class NutrIA(GrokClient):  
    def __init__(self):
        super().__init__(system_prompt="""
        You are an expert nutrition assistant. 
        Your task is to read the provided database data and explain it to the user clearly, kindly, and concisely. 
        STRICT RULE: When asking for a especific food You will base your responses ONLY on the provided data. If there is no data, state that you do not know. Respond in English. ONLY use other info if the user ask you for advice or recomendations, but never when they ask for the macros of a specific food. You can use other data appart form the database when the user chats with you.
        """)

    def preguntar(self, mensaje: str) -> str:
        respuesta = super().preguntar(mensaje)
        return respuesta

    def consultar(self, alimento: str) -> dict:
     
       # Busca en la API y le indica a la IA que promedie o encuentre los macros más comunes,
       # devolviéndolos en un formato estructurado.
       
        print(f"\nSearching for '{alimento}' in the FatSecret database...")
        
        datos_crudos = obtener_datos_fatsecret(alimento)
        
        prompt_new = f"""
        The user requested information about '{alimento}'.
        Here are the top results from the FatSecret database:
        {datos_crudos}
        
        Task 1: Analyze these options and pick the most common one, or calculate the average values for calories, carbs (g), protein (g), and fat (g).
        Task 2: Write a friendly 1-2 sentence explanation of your choice in English.
        Task 3: Output the result STRICTLY as a JSON object. Do not include any other text outside the JSON structure.

        Expected JSON format exactly like this:
        {{
            "explanation": "I found a few options for the burrito and calculated the average",
            "calories": 350,
            "carbs": 40.5,
            "protein": 15.0,
            "fat": 12.5
        }}
        """
        
        respuesta = self.preguntar(prompt_new)
        
        # Expresión regular para extraer de forma segura el JSON de la respuesta de la IA
        match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if match:
            try:
                datos = json.loads(match.group(0))
                # Asegurar el tipo de dato y que este presente en la informacion de la api
                for key in ["calories", "carbs", "protein", "fat"]:
                    if key not in datos:
                        datos[key] = 0
                if "explanation" not in datos:
                    datos["explanation"] = "Here is the parsed data."
                return datos
            except json.JSONDecodeError:
                pass
        
        # Respaldo en caso de que la IA falle al generar un JSON válido
        return {
            "explanation": f"I couldn't determine exact averages, but here is the raw data:\n{datos_crudos}",
            "calories": 0, "carbs": 0, "protein": 0, "fat": 0
        }