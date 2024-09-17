# automations/monitor_assinatura.py

import time
import logging

def monitor_assinatura(notion, running_event, database_ids):
    logging.info("Iniciando automação 'monitor_assinatura'")

    try:
        assinatura_db_id = database_ids.get("Assinatura")
        transacao_db_id = database_ids.get("Transação")

        if not all([assinatura_db_id, transacao_db_id]):
            logging.error("Um ou mais databases não foram encontrados. Verifique os nomes dos databases.")
            return

        while running_event.is_set():
            new_pages = get_new_pages(notion, assinatura_db_id)

            for page in new_pages:
                process_new_assinatura_page(notion, page, transacao_db_id)

            for _ in range(60):
                if not running_event.is_set():
                    break
                time.sleep(1)

    except Exception as e:
        logging.error(f"Ocorreu um erro na automação 'monitor_assinatura': {e}", exc_info=True)

def get_new_pages(notion, database_id):
    new_pages = []
    try:
        response = notion.databases.query(
            **{
                "database_id": database_id,
                "filter": {
                    "property": "Processado",
                    "checkbox": {
                        "equals": False
                    }
                }
            }
        )
        new_pages.extend(response["results"])
    except Exception as e:
        logging.error(f"Erro ao obter novas páginas: {e}", exc_info=True)
    return new_pages

def process_new_assinatura_page(notion, assinatura_page, transacao_db_id):
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

        # Obtém o valor da propriedade "Banco"
        banco_relations = []
        if assinatura_properties.get("Banco") and assinatura_properties["Banco"]["relation"]:
            banco_relations = assinatura_properties["Banco"]["relation"]

        # Obtém o valor da propriedade "Cartão de Crédito"
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
            },
            "Recorrente": {
                "checkbox": True
            },
        }

        # Adiciona "Valor" se disponível
        if valor is not None:
            new_page_properties["Valor"] = {
                "number": valor
            }

        # Adiciona "Banco" se disponível, convertendo para lista se for um set
        if banco_relations:
            if isinstance(banco_relations, set):
                banco_relations = list(banco_relations)
            new_page_properties["Banco"] = {
                "relation": banco_relations
            }

        # Adiciona "Cartão de Crédito" se disponível, convertendo para lista se for um set
        if cartao_relations:
            if isinstance(cartao_relations, set):
                cartao_relations = list(cartao_relations)
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

        # Cria a nova página em "Transação"
        new_transacao_page = notion.pages.create(
            parent={"database_id": transacao_db_id},
            properties=new_page_properties
        )

        logging.info(f"Criada nova transação: {new_transacao_page['id']} para a assinatura: {assinatura_name}")

        # Marca a página de "Assinatura" como processada
        notion.pages.update(
            page_id=assinatura_page_id,
            properties={
                "Processado": {
                    "checkbox": True
                }
            }
        )

        logging.info(f"Página de 'Assinatura' {assinatura_name} marcada como processada.")

        return True  # Página processada com sucesso

    except Exception as e:
        logging.error(f"Falha ao processar a página de 'Assinatura' {locals().get('assinatura_page_id', 'ID não disponível')}: {e}", exc_info=True)
        return False