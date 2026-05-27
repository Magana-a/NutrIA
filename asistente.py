import requests
import os
import json
from datetime import datetime
from openai import OpenAI
from grok_client import GrokClient
from dotenv import load_dotenv

FS_CLIENT_ID = "0c736cfe1eb640b9828ce01ce5b03ce0"
FS_CLIENT_SECRET = "d4d3b2bf2cc74b65bb73cb0112fc5d2f"

def obtener_datos_fatsecret(alimento: str) -> str:
    """Connects to FatSecret, searches for the food, and returns raw text info."""
    token_url = "https://oauth.fatsecret.com/connect/token"
    
    # 1. Safely request the Access Token
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

    # 2. Search for the Food
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
        
        for food in resultados[:3]:
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
        STRICT RULE: You will base your responses ONLY on the provided data. If there is no data, state that you do not know. Do not invent calories or macronutrients. Respond in English.
        """)

    def preguntar(self, mensaje: str) -> str:
        respuesta = super().preguntar(mensaje)
        return respuesta

    def consultar_api_y_explicar(self, alimento: str) -> str:
        """
        Searches the API and passes the data to the AI to read.
        """
        print(f"\n Searching for '{alimento}' in the FatSecret database...")
        
       
        datos_crudos = obtener_datos_fatsecret(alimento)
        
        prompt_new = (
            f"The user requested information about '{alimento}'.\n"
            f"Here is the data extracted directly from the FatSecret database:\n"
            f"{datos_crudos}\n\n"
            f"Please read this data and present it in an organized and conversational way in English. "
            f"State the calories and main macronutrients based only on this text."
        )
        
        return self.preguntar(prompt_new)