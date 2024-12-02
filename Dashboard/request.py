import requests

# Token da API
TOKEN = "demo"
CITY = "sao-paulo"  # Nome da cidade

#http://api.waqi.info/feed/shanghai/?token=demo

# URL da API
url = f"http://api.waqi.info/feed/{CITY}/?token={TOKEN}"

# Realizar a requisição
response = requests.get(url)

# Processar a resposta
if response.status_code == 200:
    data = response.json()
    if data["status"] == "ok":
        # Extrair poluente CO e temperatura
        co = data["data"]["iaqi"].get("co", {}).get("v", "Dados indisponíveis")
        temperature = data["data"]["iaqi"].get("t", {}).get("v", "Dados indisponíveis")

        print(f"Dados para São Paulo:")
        print(f"Monóxido de Carbono (CO): {co}")
        print(f"Temperatura (T): {temperature}°C")
    else:
        print(f"Erro na API: {data.get('data', 'Resposta inválida')}")
else:
    print(f"Erro HTTP: {response.status_code}")