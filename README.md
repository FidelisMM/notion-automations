# Notion Automation System

Este projeto é um sistema que automatiza processos no Notion utilizando a API do Notion. Ele monitora e processa páginas em databases específicos, criando novas transações com base em assinaturas.

Este projeto é voltado para o template **Finance OS**.

## Funcionalidades

- Monitora o database de assinaturas no Notion.
- Cria novas transações com base nas assinaturas encontradas.
- Marca as assinaturas como processadas após a criação das transações.

## Requisitos

- Python 3.8+
- Conta no Notion e token de integração
- Heroku CLI (opcional, para deploy no Heroku)

## Instalação

1. Clone o repositório:

    ```sh
    git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
    cd NOME_DO_REPOSITORIO
    ```

2. Crie um ambiente virtual e ative-o:

    ```sh
    python -m venv .venv
    source .venv/bin/activate  # No Windows, use .venv\Scripts\activate
    ```

3. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```

4. Crie um arquivo `.env` na raiz do projeto e adicione o seu token do Notion:

    ```env
    NOTION_TOKEN=seu_token_do_notion
    ```

## Uso

1. Execute o script principal:

    ```sh
    python main.py
    ```

2. O sistema começará a monitorar o database de assinaturas e processar novas páginas conforme necessário.

## Estrutura do Projeto

- `main.py`: Script principal que inicializa o cliente do Notion e as threads de automação.
- `automations/monitor_assinatura.py`: Contém a lógica para monitorar e processar assinaturas.
- `utils.py`: Funções utilitárias, como `get_database_id_by_name`.

## Deploy no Heroku

1. Faça login no Heroku:

    ```sh
    heroku login
    ```

2. Crie um novo aplicativo no Heroku:

    ```sh
    heroku create nome-do-seu-app
    ```

3. Adicione o repositório remoto do Heroku:

    ```sh
    git remote add heroku https://git.heroku.com/nome-do-seu-app.git
    ```

4. Faça o deploy para o Heroku:

    ```sh
    git push heroku master
    ```

5. Configure as variáveis de ambiente no Heroku:

    ```sh
    heroku config:set NOTION_TOKEN=seu_token_do_notion
    ```

6. Inicie o aplicativo no Heroku:

    ```sh
    heroku ps:scale web=1
    ```

## Mais Informações

Para mais templates do Notion, visite [Flow Notion](https://flownotion.framer.website/).