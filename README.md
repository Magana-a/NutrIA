NutrIA es una sistente de nutricion que integra la ia Groq y l api de Fatsecret.
Al utilizar diversas dependencia externas, es necesario seguir una serie de pasos para poder ejecutar el programa de forma optima.


Paso 1: Instalar las dependencias necesarias
El proyecto utiliza varias librerías externas. Es necesario abrir la terminal, asegurarse de tener Python instalado y ejecutar el siguiente comando para instalar las dependencias:

Bash
pip install streamlit requests openai python-dotenv

Paso 2: Obtener las credenciales de FatSecret y registrar la IP
Para que la búsqueda de alimentos funcione, es necesario conectarse a la API de FatSecret:

Se debe ingresar al portal para desarrolladores de FatSecret Developer y crear una cuenta gratuita.

Se requiere crear una nueva aplicación dentro del panel de control.

Se necesita obtener el Client ID y el Client Secret.

IMPORTANTE: Por medidas de seguridad de FatSecret, se necesita registrar la dirección IP pública en la configuración de la aplicación dentro de su portal. Si no se registra la IP, la API bloqueará las peticiones y la aplicación no podrá buscar alimentos.

Paso 3: Obtener la API Key de la Inteligencia Artificial (Groq/xAI)
Para que el chat inteligente funcione, se requiere una clave de acceso:

Se debe crear una cuenta en la plataforma del proveedor de IA utilizado (Groq o xAI).

Se necesita generar una nueva API Key y copiarla.

Paso 4: Configurar el archivo de variables de entorno (.env)
Por seguridad, las claves de las APIs no están incluidas en el código fuente. Se debe crear un archivo local para almacenarlas:

En la carpeta principal del proyecto (donde se encuentra el archivo main.py), se necesita crear un archivo llamado exactamente .env (con el punto al inicio).

Se debe abrir el archivo y pegar las credenciales con el siguiente formato, reemplazando los textos de ejemplo por las claves reales:


XAI_API_KEY=pegar_aqui_api_key_de_la_ia
FS_CLIENT_ID=pegar_aqui_client_id_de_fatsecret
FS_CLIENT_SECRET=pegar_aqui_client_secret_de_fatsecret


Paso 5: Ejecutar la aplicación
Una vez instaladas las dependencias y configurado el archivo .env, la aplicación está lista para iniciarse. En la terminal, asegurándose de estar en la carpeta del proyecto, se debe ejecutar:

Bash
streamlit run main.py
Este comando abrirá automáticamente una pestaña en el navegador web (usualmente en http://localhost:8501) con la interfaz gráfica de NutrIA lista para su uso.
