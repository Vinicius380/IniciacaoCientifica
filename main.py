from datetime import datetime, timezone
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt

# ********************** CONEXÃO COM O BANCO DE DADOS **********************

app = Flask("registros")     # Nome do aplicativo.

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Configura o SQLAlchemy para rastrear modificações. 

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://senai%40134@127.0.0.1/bd_medicao'

mybd = SQLAlchemy(app)      # Cria uma instância do SQLAlchemy, passando a aplicação Flask como parâmetro. 

# *************************** CONEXÃO DOS SENSORES ***************************
# mqtt_dados = {}

# def conexao_sensor(client, userdata, flags, rc):
#     client.subscribe("projeto_integrado/SENAI134/Cienciadedados/Grupo1")

# def msg_sensor(client, userdata, msg):
#     global mqtt_dados
    
#     valor = msg.payload.decode('utf-8')     # Decodificar a mensagem recebida de bytes para string
#     mqtt_dados = json.loads(valor)          # Decodificar de string para JSON
#     print(f'Mensagem recebida: {mqtt_dados}')
    
#     with app.app_context():         # Correlação Banco de Dados com Sensor. 
#         try:
#             temperatura = mqtt_dados.get('temperature')
#             pressao = mqtt_dados.get('pressure')
#             altitude = mqtt_dados.get('altitude')
#             umidade = mqtt_dados.get('humidity')
# <<<<<<< HEAD
#             co2 = mqtt_dados.get('CO2')
#             poeira = mqtt_dados.get("particula1")
# =======
#             co2 = mqtt_dados.get('co2') #co2
#             poeira = 0 # mqtt_dados.get('poeira1')
# >>>>>>> 82f5336b5a4ceda8f8a6e5f21d61593e1449f236
#             tempo_registro = mqtt_dados.get('timestamp')
#             regiao = 'Grande ABC'
            
#             if tempo_registro is None:
#                 print("Timestamp não encontrado")
#                 return
            
#             try:
#                 tempo_oficial = datetime.fromtimestamp(int(tempo_registro), tz=timezone.utc)
            
#             except (ValueError, TypeError) as e:
#                 print(f"Erro ao converter timestamp: {str(e)}")
#                 return
#             # Criar para objeto que vai simular a tabela do banco. 
#             novos_dados = Registro(
#                 temperatura = temperatura,
#                 pressao = pressao,
#                 altitude = altitude,
#                 umidade = umidade,
#                 co2 = co2,
#                 poeira = poeira,
#                 tempo_registro = tempo_oficial,
#                 regiao = regiao
#             )
            
#             # Adicionar novo registro ao banco.
#             mybd.session.add(novos_dados)
#             mybd.session.commit()
#             print("Os dados foram inseridos com sucesso no banco de dados!")
        
#         except Exception as e:
#             print(f"Erro ao processar os dados do MQTT: {str(e)}")
#             mybd.session.rollback()

# mqtt_client = mqtt.Client()
# mqtt_client.on_connect = conexao_sensor
# mqtt_client.on_message = msg_sensor
# mqtt_client.connect("test.mosquitto.org", 1883, 60)

# def start_mqtt():
#     mqtt_client.loop_start()
    
class Registro(mybd.Model):
    __tablename__ = 'tb_registro'
    id = mybd.Column(mybd.Integer, primary_key=True, autoincrement=True)
    temperatura = mybd.Column(mybd.Numeric(10, 2))
    pressao = mybd.Column(mybd.Numeric(10, 2))
    altitude = mybd.Column(mybd.Numeric(10, 2))
    umidade = mybd.Column(mybd.Numeric(10, 2))
    co2 = mybd.Column(mybd.Numeric(10, 2))
    poeira = mybd.Column(mybd.Numeric(10, 2))
    tempo_registro = mybd.Column(mybd.DateTime)
    regiao = mybd.Column(mybd.String(100))
    

# Seleciona todos os registros
@app.route('/registro', methods=['GET'])
def selecionar_registros():
    registros = Registro.query.all()
    registros_json = [registro.to_json() for registro in registros]
    
    return gera_response(200, 'registros', registros_json)


# Seleciona um registro por Id específico
@app.route('/registro/<id>', methods=['GET'])
def selecionar_registro_por_id(id):
    registro = Registro.query.filter_by(id=id).first()
    
    if registro:
        registro_json = registro.to_json()
        return gera_response(200, 'registro', registro_json)
    else:
        return gera_response(400, 'registro', {}, 'Registro não encontrado')
    
# Deleta um registro por Id específico
@app.route('/registro/<id>', methods=['DELETE'])
def deletar_registro_por_id(id):
    registro = Registro.query.filter_by(id=id).first()
    
    if registro:
        try:
            mybd.session.delete(registro)
            mybd.session.commit()
            return gera_response(200, 'registro', registro.to_json(), 'Registro deletado!')
        except Exception as error:
            print(f'Erro: {error}')
            mybd.session.rollback()
            return gera_response(400, 'registro', {}, 'Erro ao deletar registro.')
    else:
        return gera_response(400, 'registro', {}, 'Registro não encontrado.')
        
    
@app.route('/dados', methods=['POST'])
def criar_dados():
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'error': 'Nenhum dado foi fornecido'}), 400   
        
        print(f'Dados Recebidos": {dados}')
        temperatura = dados.get('temperatura')  
        pressao = dados.get('pressao')  
        altitude = dados.get('altitude')  
        umidade = dados.get('umidade')  
        co2 = dados.get('co2')  
        poeira = dados.get('poeira')  
        timestamp_unix = dados.get('tempo_registro')
        regiao = dados.get('regiao')
        
        try:
            tempo_oficial = datetime.fromtimestamp(int(timestamp_unix), tz=timezone.utc)
        except Exception as e:
            print('Erro', e)
            return jsonify({'error': 'Timestamp inválido'}), 400 
        
        novo_registro = Registro(
            temperatura=temperatura,
            pressao=pressao,
            altitude=altitude,
            umidade=umidade,
            co2=co2,
            poeira=poeira,
            tempo_registro=tempo_oficial,
            regiao = regiao
        )
        
        mybd.session.add(novo_registro)
        print('Adicionando novo registro...')
        
        mybd.session.commit()
        print('Dados inseridos no banco de dados com sucesso!')
        
        return jsonify({'mensagem': 'Dados recebidos com sucesso'}), 201
        
    except Exception as e:
        print(f'Erro ao processar a solicitação', e)
        mybd.session.rollback()
        return jsonify({'erro': 'Falha ao processar os dados'}), 500
    
    
    
def gera_response(status, nome_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


      
if __name__ == '__main__':
    with app.app_context():
        mybd.create_all()
        
        app.run(port=5000, host="localhost", debug=True)
