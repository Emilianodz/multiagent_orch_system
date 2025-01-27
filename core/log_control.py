import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, time
import json
import os
import subprocess
import platform
from colorama import init, Fore, Style

# Configuración de logs con rotación
LOG_FILE = "orchestrator_logs.log"
handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Configurar el logger root
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)

class LogManager:
    @staticmethod
    def log_interaction(log_data: dict):
        """
        Registra una interacción en el archivo de logs.
        """
        try:
            log_entry = json.dumps(log_data, separators=(',', ':'))
            # logging.getLogger('root').info(log_entry)
            
            # Mostrar solo un mensaje simple en la consola
            logger = logging.getLogger('orchestrator')
            logger.info("=== Flujo de procesamiento completado ===")
            
        except Exception as e:
            logging.error(f"Error al registrar el log: {str(e)}")

    @staticmethod
    def create_log_entry(user_id: str, conversation_id: str, query: str, router_query: str,
                         router_response: dict, final_response: str) -> dict:
        """
        Crea una entrada de log con los datos de la interacción.
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
        Inicia un visor en tiempo real para leer logs en una nueva ventana.
        """
        try:
            # Crear un script temporal para el visor de logs
            viewer_script = '''
import time
import os
from colorama import init, Fore, Style

# Inicializar colorama para Windows
init()

log_file = 'orchestrator_logs.log'
print(f'Leyendo logs en tiempo real desde: {log_file}')
print('Esperando nuevos logs...')

def print_colored_log(line):
    """Imprime el log con color si es un error"""
    if '"levelname":"ERROR"' in line or ' - ERROR - ' in line:
        print(Fore.RED + line.strip() + Style.RESET_ALL)
    else:
        print(line.strip())

with open(log_file, 'r') as f:
    f.seek(0, os.SEEK_END)
    while True:
        line = f.readline()
        if line:
            print_colored_log(line)
        time.sleep(0.5)
'''
            # Asegurarse de que colorama esté instalado
            try:
                import colorama
            except ImportError:
                subprocess.check_call(['pip', 'install', 'colorama'])

            # Guardar el script en un archivo temporal
            with open('temp_log_viewer.py', 'w', encoding='utf-8') as f:
                f.write(viewer_script.strip())

            # Ejecutar el script en una nueva ventana según el sistema operativo
            if platform.system() == "Windows":
                subprocess.Popen('start cmd /k python temp_log_viewer.py', shell=True)
            else:  # Para Linux y MacOS
                terminal_command = 'gnome-terminal' if platform.system() == "Linux" else 'open -a Terminal'
                subprocess.Popen(f'{terminal_command} -- python3 temp_log_viewer.py', shell=True)

        except Exception as e:
            logging.error(f"Error al iniciar el visor de logs: {str(e)}")
