import os
import requests
from dotenv import load_dotenv

load_dotenv()

n8n_url = os.getenv('N8N_WEBHOOK_URL')
print(f"Testing URL: {n8n_url}")

if not n8n_url:
    print("❌ No URL found")
    exit(1)

try:
    response = requests.post(n8n_url, json={"chatInput": "Hola, esto es una prueba de conexión"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Conexión exitosa!")
    else:
        print("❌ Falló la conexión")
except Exception as e:
    print(f"❌ Error: {e}")
