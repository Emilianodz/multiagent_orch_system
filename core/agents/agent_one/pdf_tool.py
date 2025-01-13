from llama_index.core.readers import SimpleDirectoryReader
from pathlib import Path
import os


# CONFIGURACIÓN
# Definir el directorio de los PDFs (puedes cambiar la ruta según tus necesidades)
CURRENT_DIR = Path(__file__).parent
PDF_DIR = CURRENT_DIR / "unic_pdf"


# FUNCIONES PRINCIPALES
def load_pdfs_from_directory(pdf_directory: Path):
    """
    Lee todos los archivos PDF en un directorio y los convierte en documentos procesables.

    Args:
        pdf_directory (Path): Ruta del directorio donde están los PDFs.

    Returns:
        List[Document]: Lista de documentos cargados desde los PDFs.
    """
    if not pdf_directory.exists() or not pdf_directory.is_dir():
        raise ValueError(f"El directorio {pdf_directory} no existe o no es válido.")

    # Leer los documentos PDF usando SimpleDirectoryReader
    print(f"Cargando documentos desde la carpeta: {pdf_directory}")
    documents = SimpleDirectoryReader(pdf_directory, file_extractor="pdf").load_data()
    
    print(f"Se cargaron {len(documents)} documentos.")
    return documents


def analyze_pdf_content(documents, query: str) -> str:
    """
    Analiza los documentos PDF y responde a una consulta específica basada en el contenido.

    Args:
        documents (List[Document]): Lista de documentos cargados.
        query (str): Consulta realizada por el usuario.

    Returns:
        str: Respuesta basada en el contenido de los documentos.
    """
    if not documents:
        return "No se encontraron documentos para analizar."

    # Concatenar todo el texto de los documentos en un único contexto
    full_text = "\n".join([doc.get_text() for doc in documents])

    # Crear un prompt basado en el contenido y la consulta
    prompt = (
        f"Eres un asistente experto en análisis de contenido. A continuación tienes información extraída "
        f"de varios documentos. Responde de manera clara y específica a la consulta del usuario.\n\n"
        f"Contenido de los documentos:\n{full_text}\n\n"
        f"Consulta: {query}\n\n"
        f"Respuesta:"
    )
    
    # Por simplicidad, puedes usar un modelo LLM para responder
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
    response = llm.invoke(prompt)

    return response.content.strip()


# EJECUCIÓN AUTOMÁTICA
if __name__ == "__main__":
    print("=== Lector de PDFs con LlamaIndex ===")
    
    # Cargar documentos desde la carpeta unic_pdf
    try:
        documents = load_pdfs_from_directory(PDF_DIR)
    except ValueError as e:
        print(str(e))
        exit(1)

    # Solicitar consulta al usuario
    consulta = input("Introduce tu consulta sobre el contenido de los PDFs: ").strip()
    if consulta:
        print("\nAnalizando los documentos...")
        respuesta = analyze_pdf_content(documents, consulta)
        print(f"\nRespuesta generada:\n{respuesta}")
    else:
        print("No se proporcionó ninguna consulta.")
