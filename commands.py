import sys
from core.vector_orch_library import initialize_vector_library as initialize_orchestrator_library
from core.agents.agent_one.vector_library import initialize_vector_library as initialize_agent_one_library
from core.agents.agent_two.vector_library import initialize_vector_library as initialize_agent_two_library
from core.log_control import LogManager


def print_help():
    """
    Imprime la lista de comandos disponibles y su descripción.
    """
    help_text = """
=== COMANDOS DISPONIBLES ===
1. initialize_vectors [orchestrator|agent_one|agent_two|all]
    - Descripción: Inicializa las bibliotecas de vectores.
      - 'orchestrator': Inicializa la biblioteca del orquestador.
      - 'agent_one': Inicializa la biblioteca del Agente 1.
      - 'agent_two': Inicializa la biblioteca del Agente 2.
      - 'all': Inicializa todas las bibliotecas.
    - Uso: python commands.py initialize_vectors orchestrator
    
2. logs
    - Descripción: Abre el visor de logs.
    - Uso: python commands.py logss

=== NOTAS ===
- Asegúrate de que las carpetas correspondientes ('documents/') contengan archivos antes de ejecutar.
- Este script está diseñado para ejecutar tareas administrativas directamente desde la consola.
"""
    print(help_text)


def initialize_orchestrator():
    """
    Inicializa la biblioteca de vectores del orquestador.
    """
    print("Inicializando la biblioteca de vectores del orquestador...")
    try:
        vector_library = initialize_orchestrator_library()
        print("¡Biblioteca del orquestador inicializada con éxito!")
        print(f"Documentos cargados: {len(vector_library.storage_context.docstore)}")
    except Exception as e:
        print(f"Error al inicializar la biblioteca del orquestador: {str(e)}")


def initialize_agent_one():
    """
    Inicializa la biblioteca de vectores del Agente 1.
    """
    print("Inicializando la biblioteca de vectores del Agente 1...")
    try:
        vector_library = initialize_agent_one_library()
        print("¡Biblioteca del Agente 1 inicializada con éxito!")
        print(f"Documentos cargados: {len(vector_library.storage_context.docstore)}")
    except Exception as e:
        print(f"Error al inicializar la biblioteca del Agente 1: {str(e)}")


def initialize_agent_two():
    """
    Inicializa la biblioteca de vectores del Agente 2.
    """
    print("Inicializando la biblioteca de vectores del Agente 2...")
    try:
        vector_library = initialize_agent_two_library()
        print("¡Biblioteca del Agente 2 inicializada con éxito!")
        print(f"Documentos cargados: {len(vector_library.storage_context.docstore)}")
    except Exception as e:
        print(f"Error al inicializar la biblioteca del Agente 2: {str(e)}")


def initialize_all():
    """
    Inicializa todas las bibliotecas de vectores.
    """
    print("Inicializando todas las bibliotecas de vectores...")
    initialize_orchestrator()
    initialize_agent_one()
    initialize_agent_two()
    print("¡Todas las bibliotecas inicializadas con éxito!")


def view_logs():
    """
    Comando para abrir el visor de logs en una nueva ventana
    """
    LogManager.start_log_viewer()


if __name__ == "__main__":
    # Verificar argumentos de la consola
    if len(sys.argv) < 2:
        print("Error: No se proporcionó ningún comando.")
        print_help()
        sys.exit(1)

    # Obtener el comando desde los argumentos
    command = sys.argv[1].strip().lower()

    if command == "initialize_vectors":
        # Verificar el argumento opcional para seleccionar la biblioteca
        if len(sys.argv) == 3:
            target = sys.argv[2].strip().lower()
            if target == "orchestrator":
                initialize_orchestrator()
            elif target == "agent_one":
                initialize_agent_one()
            elif target == "agent_two":
                initialize_agent_two()
            elif target == "all":
                initialize_all()
            else:
                print(f"Error: Argumento desconocido '{target}'.")
                print_help()
        else:
            print("Error: Se requiere un argumento para 'initialize_vectors'.")
            print_help()
    elif command in ["help", "--help", "-h"]:
        print_help()
    elif command == "logs":
        view_logs()
    else:
        print(f"Error: Comando desconocido '{command}'.")
        print_help()
        sys.exit(1)
