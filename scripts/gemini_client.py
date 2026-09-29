import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["GEMINI_API_KEY"]
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
)


def llamar_gemini(prompt: str, intentos: int = 3) -> str:
    for intento in range(intentos):
        try:
            response = requests.post(
                f"{API_URL}?key={API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            texto = data["candidates"][0]["content"]["parts"][0]["text"]
            return texto
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as error:
            if intento < intentos - 1:
                espera = 2 ** (intento + 1)
                print(f"Timeout/conexión falló, reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise
        except requests.exceptions.HTTPError as error:
            if response.status_code == 503 and intento < intentos - 1:
                espera = 2 ** (intento + 1)
                print(f"Gemini devolvió 503, reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise
