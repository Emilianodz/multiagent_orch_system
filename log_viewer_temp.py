
import sys
import time
import os

log_file = r"C:\Users\ediaz\OneDrive\Escritorio\agent_dev\multiagent_orch\multiagent_orch\orchestrator_logs.log"
print("=== LOG VIEWER INICIADO ===")
print(f"Monitoreando archivo: {log_file}")
print("Presiona Ctrl+C para cerrar")

try:
    # Mostrar logs existentes
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                print("\nLogs existentes:")
                print(content)
            else:
                print("\nArchivo de logs vacío")
    
    # Monitorear nuevos logs
    last_size = os.path.getsize(log_file) if os.path.exists(log_file) else 0
    
    while True:
        if os.path.exists(log_file):
            current_size = os.path.getsize(log_file)
            if current_size > last_size:
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_content = f.read()
                    print(new_content, end='')
                last_size = current_size
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nCerrando Log Viewer...")
except Exception as e:
    print(f"Error: {str(e)}")
    input("Presiona Enter para cerrar...")  # Mantener la ventana abierta en caso de error
