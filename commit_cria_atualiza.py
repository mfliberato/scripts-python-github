import requests
from requests.auth import HTTPBasicAuth
import base64

def commit_file_to_repositories(access_token, username, repo_names, file_path, commit_message, file_content, new_branch_name, base_branch='main'):
    url_template = 'https://api.github.com/repos/{}/{}/{}'
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    for repo_name in repo_names:
        try:
            # Obter o SHA do commit mais recente da branch base
            branch_url = url_template.format(username, repo_name, f'git/ref/heads/{base_branch}')
            response = requests.get(branch_url, headers=headers)
            
            if response.status_code == 200:
                base_sha = response.json()['object']['sha']

                # Criar uma nova branch a partir do commit mais recente
                new_branch_url = url_template.format(username, repo_name, 'git/refs')
                new_branch_data = {
                    'ref': f'refs/heads/{new_branch_name}',
                    'sha': base_sha
                }
                response = requests.post(new_branch_url, headers=headers, json=new_branch_data)
                
                if response.status_code == 201:
                    print(f"Branch {new_branch_name} criada com sucesso no repositório {repo_name}.")
                    
                    # Atualizar o URL para a nova branch
                    contents_url = url_template.format(username, repo_name, f'contents/{file_path}?ref={new_branch_name}')
                    
                    # Verifique se o arquivo já existe
                    response = requests.get(contents_url, headers=headers)
                    
                    if response.status_code == 200:
                        # File exists, update it
                        sha = response.json()['sha']
                        update_data = {
                            'message': commit_message,
                            'content': base64.b64encode(file_content.encode()).decode(),
                            'sha': sha,
                            'branch': new_branch_name
                        }
                        response = requests.put(contents_url, headers=headers, json=update_data)
                        if response.status_code == 200:
                            print(f"Arquivo {file_path} atualizado com sucesso no repositório {repo_name}.")
                        else:
                            print(f"Falha ao atualizar o arquivo {file_path} no repositório {repo_name}: {response.json()}")
                    elif response.status_code == 404:
                        # File does not exist, create it
                        create_data = {
                            'message': commit_message,
                            'content': base64.b64encode(file_content.encode()).decode(),
                            'branch': new_branch_name
                        }
                        response = requests.put(contents_url, headers=headers, json=create_data)
                        if response.status_code == 201:
                            print(f"Arquivo {file_path} criado com sucesso no repositório {repo_name}.")
                        else:
                            print(f"Falha ao criar o arquivo {file_path} no repositório {repo_name}: {response.json()}")
                    else:
                        print(f"Erro ao acessar o repositório {repo_name}: {response.json()}")
                else:
                    print(f"Falha ao criar a branch {new_branch_name} no repositório {repo_name}: {response.json()}")
            else:
                print(f"Erro ao acessar a branch base {base_branch} no repositório {repo_name}: {response.json()}")
        
        except Exception as e:
            print(f"Falha ao acessar o repositório {repo_name}: {e}")

# Substitua por seu token de acesso pessoal do GitHub
access_token = 'SEU_TOKEN'
# Substitua por seu nome de usuário
username = 'USER_NAME'
# Lista de repositórios onde o arquivo será adicionado/atualizado
repo_names = ['repo1', 'repo2', 'repo3']
# Nome e conteúdo do novo arquivo
file_path = 'caminho/pasta/arquivo.txt'
commit_message = 'mensagem de commit'
file_content = 'conteudo arquivo'
# Nome da nova branch
new_branch_name = 'branch_name'

commit_file_to_repositories(access_token, username, repo_names, file_path, commit_message, file_content, new_branch_name)
