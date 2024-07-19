from flask import Flask, render_template, request, jsonify
import requests
import subprocess

app = Flask(__name__)

# Dados de autenticação do Trello
trello_key = ""
trello_token = ""

# Dados de autenticação do Asana
asana_token = ""

@app.route('/')
def index():
    quadros_trello = obter_quadros_do_trello()
    projetos_asana = obter_projetos_do_asana()
    return render_template('index.html', trello_boards=quadros_trello, asana_projects=projetos_asana)

@app.route('/get_lists', methods=['POST'])
def get_lists():
    board_id = request.json.get('board_id')
    if not board_id:
        return jsonify({'error': 'ID do quadro não fornecido'}), 400
    
    listas = obter_listas_do_trello(board_id)
    return jsonify(listas)

@app.route('/executar_automacao_asana', methods=['POST'])
def executar_automacao_asana():
    board_id = request.json.get('board_id')
    if not board_id:
        return jsonify({'error': 'ID do quadro não fornecido'}), 400
    
    try:
        result = subprocess.run(['python', 'Automação_com_Asana.py', board_id], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e), 500

def obter_quadros_do_trello():
    url_quadros = f"https://api.trello.com/1/members/me/boards"
    params_trello = {
        'key': trello_key,
        'token': trello_token
    }

    response = requests.get(url_quadros, params=params_trello)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao obter quadros do Trello: {response.status_code} - {response.text}")
        return []

def obter_listas_do_trello(board_id):
    url_listas = f"https://api.trello.com/1/boards/{board_id}/lists"
    params_trello = {
        'key': trello_key,
        'token': trello_token
    }

    response = requests.get(url_listas, params=params_trello)
    if response.status_code == 200:
        return [{'id': lista['id'], 'name': lista['name']} for lista in response.json()]
    else:
        print(f"Erro ao obter listas do Trello: {response.status_code} - {response.text}")
        return []

def obter_projetos_do_asana():
    url_projetos = "https://app.asana.com/api/1.0/projects"
    headers_asana = {
        "Authorization": f"Bearer {asana_token}"
    }

    response = requests.get(url_projetos, headers=headers_asana)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Erro ao obter projetos do Asana: {response.status_code} - {response.text}")
        return []

if __name__ == '__main__':
    app.run(debug=True)
