


import requests
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


class GrokClient:
    """
    Cliente base para interactuar con la API de Grok (xAI).
    Encapsula la configuración de conexión y el historial de conversación.
    """
    def __init__(self, system_prompt: str = "Eres un asistente útil."):
        """
        TODO:
        - Carga la API key desde la variable de entorno XAI_API_KEY
          usando os.getenv(). Guárdala en un atributo privado __api_key.
        - Si no existe la variable de entorno, lanza un ValueError
          con un mensaje descriptivo.
        - Crea el cliente de OpenAI apuntando a la base_url de xAI:
          "https://api.x.ai/v1"
        - Guarda el system_prompt en un atributo privado __system_prompt.
        - Inicializa el atributo historial como una lista vacía.
        - El modelo a usar es "grok-3-mini". Guárdalo en self.modelo.
        """
        self.__api_key = os.getenv("XAI_API_KEY")
        if not self.__api_key:
            raise ValueError("Error opteniendo la API key")
        self.__cliente = OpenAI(api_key=self.__api_key, base_url="https://api.groq.com/openai/v1" )
        self.__system_prompt = system_prompt
        self.historial = []
        self.modelo = "llama-3.3-70b-versatile"


    def _construir_mensajes(self) -> list:
        """
        TODO:
        Retorna la lista de mensajes en el formato que espera la API:
        - El primer elemento siempre es el system prompt:
          {"role": "system", "content": self.__system_prompt}
        - Luego agrega todos los mensajes del historial.


        Este es un método privado por convenio (prefijo _).
        """
        mensajes = [{"role": "system", "content": self.__system_prompt}]
        mensajes.extend(self.historial)
        return mensajes


    def preguntar(self, mensaje: str) -> str:
        """
        TODO:
        1. Agrega el mensaje del usuario al historial con role "user".
        2. Llama a self.__cliente.chat.completions.create() con:
               model=self.modelo
               messages=self._construir_mensajes()
        3. Extrae el texto desde respuesta.choices[0].message.content
        4. Agrega la respuesta al historial con role "assistant".
        5. Retorna el texto de la respuesta.
        """
        self.historial.append({"role": "user", "content": mensaje})
        respuesta = self.__cliente.chat.completions.create(
            model=self.modelo,
            messages=self._construir_mensajes()
        )
        texto = respuesta.choices[0].message.content
        self.historial.append({"role": "assistant", "content": texto})
        return texto


    def limpiar_historial(self):
        """Reinicia el historial de conversación."""
        self.historial = []


    def __str__(self):
        """
        TODO:
        Retorna una representación legible, por ejemplo:
        GrokClient | modelo: grok-3-mini | mensajes en historial: 4
        """
        return f"GrokClient | modelo: {self.modelo} | mensajes en historial: {len(self.historial)}"

