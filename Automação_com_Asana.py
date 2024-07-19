import requests
import sys
from datetime import datetime, timedelta

# Dados de autenticação do Trello
trello_key = ""
trello_token = ""

# Dados de autenticação do Asana
asana_token = ""

# ID do quadro do Trello (passado como argumento)
board_id = sys.argv[1]

# URL base da API do Asana e Trello
asana_base_url = "https://app.asana.com/api/1.0"
trello_base_url = "https://api.trello.com/1"

# Configuração do cabeçalho com o token de autenticação do Asana
headers_asana = {
    "Authorization": f"Bearer {asana_token}",
    "Content-Type": "application/json"
}

def find_project_by_name(project_name):
    projects_url = f"{asana_base_url}/projects"
    response = requests.get(projects_url, headers=headers_asana)
    if response.status_code == 200:
        projects_data = response.json()['data']
        for project in projects_data:
            if project['name'] == project_name:
                return project['gid']
    return None

def create_project(project_name, workspace_gid):
    create_project_url = f"{asana_base_url}/projects"
    data = {
        "data": {
            "name": project_name,
            "workspace": workspace_gid
        }
    }
    response_create = requests.post(create_project_url, headers=headers_asana, json=data)
    if response_create.status_code == 201:
        return response_create.json()['data']['gid']
    return None

def get_workspace_gid():
    workspaces_url = f"{asana_base_url}/workspaces"
    response_ws = requests.get(workspaces_url, headers=headers_asana)
    if response_ws.status_code == 200:
        workspaces_data = response_ws.json()['data']
        if workspaces_data:
            return workspaces_data[0]['gid']
    return None

def obter_listas_do_trello(board_id):
    url_listas = f"{trello_base_url}/boards/{board_id}/lists"
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

try:
    project_name = "Novo Projeto"
    project_gid = find_project_by_name(project_name)
    
    if not project_gid:
        workspace_gid = get_workspace_gid()
        if workspace_gid:
            project_gid = create_project(project_name, workspace_gid)
            if project_gid:
                print(f"Projeto '{project_name}' criado com sucesso. GID: {project_gid}")
            else:
                print(f"Erro ao criar projeto '{project_name}'")
        else:
            print("Erro ao obter o GID do workspace")
    else:
        print(f"Usando projeto existente: {project_name} (ID: {project_gid})")
    
    if project_gid:
        listas = obter_listas_do_trello(board_id)

        # Criando seções no Asana com base nas listas do Trello
        for lista in listas:
            nome_secao = lista['name']
            payload_secao = {
                "data": {
                    "name": nome_secao
                }
            }
            asana_sections_url = f"{asana_base_url}/projects/{project_gid}/sections"
            response_secao = requests.post(asana_sections_url, headers=headers_asana, json=payload_secao)
            if response_secao.status_code == 201:
                secao_data = response_secao.json()
                print(f"Criada seção no Asana: {secao_data['data']['name']} (ID: {secao_data['data']['gid']})")

                # Obtendo cards do Trello para criar tarefas no Asana dentro da seção
                cards_url = f"{trello_base_url}/lists/{lista['id']}/cards"
                params_trello = {
                    'key': trello_key,
                    'token': trello_token
                }
                response_cards = requests.get(cards_url, params=params_trello)
                cards_trello = response_cards.json()

                for card in cards_trello:
                    due_on = card.get('due')
                    if due_on:
                        # Convertendo a data e subtraindo um dia
                        due_date = datetime.strptime(due_on, '%Y-%m-%dT%H:%M:%S.%fZ') - timedelta(days=1)
                        due_on = due_date.date().isoformat()
                    payload_tarefa = {
                        "data": {
                            "projects": [project_gid],
                            "name": card['name'],
                            "notes": card.get('desc', ""),
                            "due_on": due_on,
                            "assignee": None,
                            "memberships": [{
                                "project": project_gid,
                                "section": secao_data['data']['gid']
                            }]
                        }
                    }
                    asana_tasks_url = f"{asana_base_url}/tasks"
                    response_tarefa = requests.post(asana_tasks_url, headers=headers_asana, json=payload_tarefa)
                    if response_tarefa.status_code == 201:
                        print(f"Tarefa criada no Asana: {card['name']}")
                    else:
                        print(f"Erro ao criar tarefa no Asana: {response_tarefa.status_code} - {response_tarefa.text}")
            else:
                print(f"Erro ao criar seção no Asana: {response_secao.status_code} - {response_secao.text}")
except Exception as e:
    print(f"Erro ao executar automação: {str(e)}")
