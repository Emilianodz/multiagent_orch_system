from langchain_openai import OpenAI
from langchain.tools import Tool
import os
import dotenv

from .generation_tool import handle_generation
from .vector_library import query_vector_library, list_available_documents
from .pdf_tool import analyze_pdf_content, load_pdfs_from_directory  # Nueva importación


# Cargar las variables de entorno desde .env
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("No se encontró la clave API de OpenAI. Verifica el archivo .env.")

# Configurar el modelo LLM
llm = OpenAI(
    temperature=0.7, 
    api_key=OPENAI_API_KEY,
    model="gpt-3.5-turbo-instruct"  # o "text-davinci-003" si lo prefieres
)

docs = list_available_documents()
if 'error' in docs:
    print(f"Error: {docs['error']}")
else:
    print("Documentos encontrados")
    #print(f"Encontrados {docs['total_documents']} documentos")
    #print("\nLista de documentos:")
    #for doc in docs['documents']:
    #    print(f"- {doc}")

# Herramienta para embeddings
def embeddings_tool(query: str) -> str:
    """
    Herramienta que utiliza la biblioteca de vectores para responder consultas relacionadas.
    """
    return query_vector_library(query)

embeddings_tool = Tool(
    name="Embeddings Tool",
    func=embeddings_tool,
    description="Usar esta herramienta para buscar información relacionada o contextual."
)

# Herramienta para generación
def generation_tool(query: str) -> str:
    """
    Herramienta que genera texto basado en la consulta.
    """
    response = handle_generation(query)

    # Validar que la respuesta sea un diccionario con la clave "response"
    if isinstance(response, dict) and "response" in response:
        return response["response"]
    elif isinstance(response, str):
        # Manejar si la respuesta es un string válido
        return response
    else:
        raise ValueError(f"Formato de respuesta inesperado: {response}")

generation_tool = Tool(
    name="Generation Tool",
    func=generation_tool,
    description="Usar esta herramienta para generar texto nuevo como explicaciones o redacciones."
)


# Herramienta para análisis de PDFs
def pdf_analysis_tool(query: str) -> str:
    """
    Herramienta para analizar el contenido de PDFs y responder preguntas relacionadas.
    """
    # Cargar documentos desde la carpeta 'unic_pdf'
    from pathlib import Path
    CURRENT_DIR = Path(__file__).parent
    PDF_DIR = CURRENT_DIR / "unic_pdf"

    # Cargar los documentos y procesar la consulta
    try:
        documents = load_pdfs_from_directory(PDF_DIR)
        response = analyze_pdf_content(documents, query)
        return response
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error al procesar los PDFs: {str(e)}"

pdf_analysis_tool = Tool(
    name="PDF Analysis Tool",
    func=pdf_analysis_tool,
    description=(
        "Usar esta herramienta para analizar y responder preguntas sobre el contenido de archivos PDF "
        "ubicados en la carpeta 'unic_pdf'. Ideal para extraer información y responder consultas específicas."
    )
)

