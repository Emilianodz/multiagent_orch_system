from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
import os
import dotenv
from pathlib import Path

# Cargar las variables de entorno desde .env
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No se encontró la clave API de OpenAI. Verifica el archivo .env.")

# Obtener la ruta absoluta del directorio actual (donde está vector_library.py)
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent  # Sube un nivel hasta multiagent_orch
DATA_DIR = PROJECT_ROOT / "documents" / "doc_orch"
PERSIST_DIR = CURRENT_DIR.parent / "storage/sto_orch"


def initialize_vector_library():
    """
    Carga o crea un índice vectorial basado en documentos técnicos.

    Returns:
        VectorStoreIndex: Índice de vector cargado o creado.
    """
    if not DATA_DIR.exists():
        raise ValueError(f"No se encontró el directorio de documentos: {DATA_DIR}")

    # Verificar si existe el archivo docstore.json en el directorio storage
    docstore_path = PERSIST_DIR / "docstore.json"
    
    if not docstore_path.exists():
        # Crear un nuevo índice desde los documentos
        print("Cargando documentos desde el directorio...")
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        print(f"Se cargaron {len(documents)} documentos.")

        print("Creando un nuevo índice de vectores...")
        index = VectorStoreIndex.from_documents(documents)

        # Crear el directorio storage si no existe
        PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        
        # Guardar el índice para reutilización futura
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print(f"Índice guardado en {PERSIST_DIR}.")
    else:
        # Cargar el índice existente desde el almacenamiento persistente
        print(f"Cargando índice existente desde {PERSIST_DIR}.")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    return index


def query_vector_library(query):
    """
    Consulta el índice vectorial con un texto específico.

    Args:
        query (str): Pregunta o consulta del usuario.

    Returns:
        str: Respuesta generada a partir de la consulta.
    """
    if not PERSIST_DIR.exists():
        return "El índice no existe. Por favor, genera la biblioteca primero."
    
    # Configurar el modelo LLM
    llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

    # Cargar el índice desde el almacenamiento
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    
    # Crear el motor de consulta utilizando el modelo LLM
    query_engine = index.as_query_engine(llm=llm)

    # Realizar la consulta
    print("Consultando la biblioteca de vectores...")
    response = query_engine.query(query)
    return response.response


# ============================
# EJECUCIÓN AUTOMÁTICA
# ============================
if __name__ == "__main__":
    print("Iniciando la biblioteca de vectores...")
    
    # Inicializar la biblioteca de vectores
    vector_index = initialize_vector_library()

    # Realizar una consulta de ejemplo
    consulta = "¿Qué información tienes?"
    print("\nConsulta de ejemplo:")
    respuesta = query_vector_library(consulta)
    print(f"\nRespuesta: {respuesta}")
