# utils.py

import logging

def get_database_ids(notion, database_names):
    database_ids = {}
    for name in database_names:
        database_id = get_database_id_by_name(notion, name)
        if database_id:
            database_ids[name] = database_id
        else:
            logging.error(f"Database '{name}' não encontrado.")
    return database_ids

def get_database_id_by_name(notion, database_name):
    logging.info(f"Procurando pelo database com o nome: {database_name}")
    response = notion.search(
        query=database_name,
        filter={
            "value": "database",
            "property": "object"
        }
    )
    for result in response["results"]:
        if result["object"] == "database" and result["title"]:
            title = "".join([text["plain_text"] for text in result["title"]])
            logging.info(f"Encontrado database com título: {title}")
            if title == database_name:
                database_id = result["id"]
                logging.info(f"ID do database '{database_name}' encontrado: {database_id}")
                return database_id
    logging.error(f"Database '{database_name}' não encontrado.")
    return None

def find_mes_page(notion, mes_db_id, prox_pagamento_dt):
    try:
        # Mapeamento de meses em inglês para português
        meses_map = {
            "January": "janeiro",
            "February": "fevereiro",
            "March": "março",
            "April": "abril",
            "May": "maio",
            "June": "junho",
            "July": "julho",
            "August": "agosto",
            "September": "setembro",
            "October": "outubro",
            "November": "novembro",
            "December": "dezembro"
        }

        # Extrai o mês e ano da data
        mes_ingles = prox_pagamento_dt.strftime("%B")  # Nome do mês em inglês
        ano_curto = prox_pagamento_dt.strftime("%y")  # Ano curto (ex: 24)

        # Converte o nome do mês para português
        mes_portugues = meses_map.get(mes_ingles, mes_ingles).lower()

        # Nome final do mês no formato "outubro 24"
        mes_nome = f"{mes_portugues} {ano_curto}"

        # Define o filtro para buscar o mês no database de Mês
        response = notion.databases.query(
            database_id=mes_db_id,
            filter={
                "property": "Mês",  # Ajuste conforme o nome da propriedade de Mês
                "title": {
                    "equals": mes_nome
                }
            }
        )

        results = response.get('results', [])
        if results:
            return results[0]  # Retorna a primeira página correspondente
        else:
            logging.warning(f"Nenhuma página de mês encontrada para {mes_nome}")
            return None
    except Exception as e:
        logging.error(f"Erro ao buscar página do mês: {e}", exc_info=True)
        return None

def find_ano_page(notion, ano_db_id, prox_pagamento_dt):
    try:
        # Extrai o ano completo da data
        ano_completo = prox_pagamento_dt.strftime("%Y")  # Ex: 2024

        # Define o filtro para buscar o ano no database de Ano
        response = notion.databases.query(
            database_id=ano_db_id,
            filter={
                "property": "Ano",  # Ajuste conforme o nome da propriedade de Ano
                "title": {
                    "equals": ano_completo
                }
            }
        )

        results = response.get('results', [])
        if results:
            return results[0]  # Retorna a primeira página correspondente
        else:
            logging.warning(f"Nenhuma página de ano encontrada para {ano_completo}")
            return None
    except Exception as e:
        logging.error(f"Erro ao buscar página do ano: {e}", exc_info=True)
        return None