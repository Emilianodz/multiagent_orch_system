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