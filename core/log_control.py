import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, time
import json
import os

# Configuración de logs con rotación
LOG_FILE = "orchestrator_logs.log"
handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class LogManager:
    @staticmethod
    def log_interaction(log_data: dict):
        """
        Registra una interacción en el archivo de logs.

        Args:
            log_data (dict): Datos de la interacción a registrar.
        """
        try:
            log_entry = json.dumps(log_data, separators=(',', ':'))  # JSON compacto
            logging.info(log_entry)
        except Exception as e:
            logging.error(f"Error al registrar el log: {str(e)}")

    @staticmethod
    def create_log_entry(user_id: str, conversation_id: str, query: str, router_query: str,
                         router_response: dict, final_response: str) -> dict:
        """
        Crea una entrada de log con los datos de la interacción.

        Args:
            user_id (str): ID del usuario.
            conversation_id (str): ID de la conversación.
            query (str): Consulta original del usuario.
            router_query (str): Consulta procesada enviada al router.
            router_response (dict): Respuesta recibida del router.
            final_response (str): Respuesta final enviada al usuario.

        Returns:
            dict: Diccionario con los datos del log.
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query": query,
            "router_query": router_query,
            "router_response": router_response,
            "final_response": final_response
        }

    @staticmethod
    def start_log_viewer():
        """
        Inicia un visor en tiempo real para leer logs.
        """
        try:
            print(f"Leyendo logs en tiempo real desde: {LOG_FILE}")
            with open(LOG_FILE, "r") as log_file:
                log_file.seek(0, os.SEEK_END)  # Ir al final del archivo

                while True:
                    line = log_file.readline()
                    if line:
                        print(line.strip())
                    else:
                        time.sleep(0.5) # Esperar 0.5 segundos antes de leer de nuevo
        except Exception as e:
            logging.error(f"Error en el visor de logs: {str(e)}")
