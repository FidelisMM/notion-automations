import os
import threading
import logging
import time
import signal
from notion_client import Client
from dotenv import load_dotenv
from utils import get_database_ids

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

if NOTION_TOKEN is None:
    logging.error("O token do Notion não foi encontrado. Verifique o arquivo .env.")
    exit(1)

notion = Client(auth=NOTION_TOKEN)

from automations.monitor_assinatura import monitor_assinatura
from automations.monitor_despesa import monitor_despesa

def main():
    logging.info("Iniciando o programa principal")

    running = threading.Event()
    running.set()

    database_names = ["Assinatura", "Transação", "Mês", "Ano"]
    database_ids = get_database_ids(notion, database_names)

    t1 = threading.Thread(target=monitor_assinatura, args=(notion, running, database_ids))
    t2 = threading.Thread(target=monitor_despesa, args=(notion, running, database_ids))

    t1.start()
    t2.start()

    def signal_handler(sig, frame):
        logging.info("Programa interrompido pelo usuário. Encerrando...")
        running.clear()
        t1.join()
        t2.join()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Programa interrompido pelo usuário. Encerrando...")
    finally:
        running.clear()
        t1.join()
        t2.join()

if __name__ == "__main__":
    main()