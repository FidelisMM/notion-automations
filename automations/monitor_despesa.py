import time
import logging
from datetime import datetime
from utils import find_mes_page, find_ano_page

def monitor_despesa(notion, running_event, database_ids):
    logging.info("Iniciando automação 'monitor_despesa'")

    try:
        assinatura_db_id = database_ids.get("Assinatura")
        transacao_db_id = database_ids.get("Transação")
        mes_db_id = database_ids.get("Mês")
        ano_db_id = database_ids.get("Ano")

        if not all([assinatura_db_id, transacao_db_id, mes_db_id, ano_db_id]):
            logging.error("Um ou mais databases não foram encontrados. Verifique os nomes dos databases.")
            return

        while running_event.is_set():
            logging.info("Obtendo todas as páginas do database de Assinatura")
            all_pages = get_all_pages(notion, assinatura_db_id)

            for page in all_pages:
                logging.info(f"Processando página: {page['id']}")
                if should_create_despesa(page):
                    logging.info(f"Criando despesa para a página: {page['id']}")
                    process_assinatura_despesa(notion, page, transacao_db_id, mes_db_id, ano_db_id)
                else:
                    logging.info(f"Página {page['id']} não requer criação de despesa")

            # Verifica se o evento foi sinalizado para parar o loop
            for _ in range(60):
                if not running_event.is_set():
                    logging.info("Programa interrompido pelo usuário. Encerrando...")
                    return
                time.sleep(1)

    except Exception as e:
        logging.error(f"Ocorreu um erro na automação 'monitor_despesa': {e}", exc_info=True)

def get_all_pages(notion, database_id):
    all_pages = []
    try:
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Criar Despesa?",
                "formula": {
                    "checkbox": {
                        "equals": True
                    }
                }
            }
        )
        all_pages.extend(response["results"])
    except Exception as e:
        logging.error(f"Erro ao obter todas as páginas: {e}", exc_info=True)
    return all_pages

def should_create_despesa(assinatura_page):
    assinatura_properties = assinatura_page["properties"]
    criar_despesa = assinatura_properties.get("Criar Despesa?", {}).get("formula", {}).get("boolean")
    return criar_despesa

from datetime import datetime

def process_assinatura_despesa(notion, assinatura_page, transacao_db_id, mes_db_id, ano_db_id):
    try:
        assinatura_page_id = assinatura_page["id"]

        # Obtém as propriedades da página de "Assinatura"
        assinatura_properties = assinatura_page["properties"]

        # Exemplo: obtém o valor da propriedade "Assinatura"
        assinatura_name = ""
        if assinatura_properties.get("Assinatura"):
            assinatura_name = assinatura_properties["Assinatura"]["title"][0]["plain_text"]

        # Obtém o valor da propriedade "Valor"
        valor = None
        if assinatura_properties.get("Valor") and assinatura_properties["Valor"]["number"] is not None:
            valor = assinatura_properties["Valor"]["number"]

        # Obtém a data da propriedade "Próx. Pagamento Dados"
        prox_pagamento = None
        if assinatura_properties.get("Próx. Pagamento Dados"):
            prox_pagamento = assinatura_properties["Próx. Pagamento Dados"].get("formula", {}).get("string")

        if prox_pagamento:
            logging.info(f"Data de Próx. Pagamento Dados encontrada: {prox_pagamento}")

            # Converte a string de data para um objeto datetime
            try:
                prox_pagamento_dt = datetime.strptime(prox_pagamento, "%Y-%m-%d")
                logging.info(f"Data convertida para datetime: {prox_pagamento_dt}")
            except ValueError as ve:
                logging.error(f"Erro ao converter Próx. Pagamento Dados para datetime: {ve}")
                prox_pagamento_dt = None

        else:
            logging.warning(f"Data de Próx. Pagamento Dados não encontrada na página {assinatura_page_id}")

        # Verifica se prox_pagamento_dt não é None antes de chamar find_mes_page e find_ano_page
        mes_page = None
        ano_page = None
        if prox_pagamento_dt:
            mes_page = find_mes_page(notion, mes_db_id, prox_pagamento_dt)
            ano_page = find_ano_page(notion, ano_db_id, prox_pagamento_dt)

        # Inicializa banco_relations
        banco_relations = []
        if assinatura_properties.get("Banco") and assinatura_properties["Banco"]["relation"]:
            banco_relations = assinatura_properties["Banco"]["relation"]

        # Inicializa cartao_relations
        cartao_relations = []
        if assinatura_properties.get("Cartão de Crédito") and assinatura_properties["Cartão de Crédito"]["relation"]:
            cartao_relations = assinatura_properties["Cartão de Crédito"]["relation"]

        # Obtém o valor da propriedade "Pagamento"
        pagamento = None
        if assinatura_properties.get("Pagamento") and assinatura_properties["Pagamento"]["select"] is not None:
            pagamento = assinatura_properties["Pagamento"]["select"]["name"]

        # Prepara as propriedades para a nova página em "Transação"
        new_page_properties = {
            "Transação": {
                "title": [
                    {
                        "text": {
                            "content": f"Assinatura {assinatura_name}"
                        }
                    }
                ]
            },
            "Assinatura": {
                "relation": [
                    {
                        "id": assinatura_page_id
                    }
                ]
            },
            "Tipo": {
                "select": {
                    "name": "Saída"
                }
            }
        }

        # Adiciona "Valor" se disponível
        if valor is not None:
            new_page_properties["Valor"] = {
                "number": valor
            }

        # Adiciona "Banco" se disponível
        if banco_relations:
            new_page_properties["Banco"] = {
                "relation": banco_relations
            }

        # Adiciona "Cartão de Crédito" se disponível
        if cartao_relations:
            new_page_properties["Cartão de Crédito"] = {
                "relation": cartao_relations
            }

        # Adiciona "Pagamento" se disponível
        if pagamento is not None:
            new_page_properties["Pagamento"] = {
                "select": {
                    "name": pagamento
                }
            }

        # Adiciona "Data" se disponível
        if prox_pagamento is not None:
            new_page_properties["Data"] = {
                "date": {
                    "start": prox_pagamento
                }
            }

        # Adiciona "Mês" se disponível
        if mes_page is not None:
            new_page_properties["Mês"] = {
                "relation": [
                    {
                        "id": mes_page["id"]
                    }
                ]
            }

        # Adiciona "Ano" se disponível
        if ano_page is not None:
            new_page_properties["Ano"] = {
                "relation": [
                    {
                        "id": ano_page["id"]
                    }
                ]
            }

        # Cria a nova página em "Transação"
        new_transacao_page = notion.pages.create(
            parent={"database_id": transacao_db_id},
            properties=new_page_properties
        )

        logging.info(f"Criada nova transação: {new_transacao_page['id']} para a assinatura: {assinatura_name}")

        return True  # Página processada com sucesso

    except Exception as e:
        logging.error(f"Falha ao processar a despesa da assinatura {locals().get('assinatura_page_id', 'ID não disponível')}: {e}", exc_info=True)
        return False