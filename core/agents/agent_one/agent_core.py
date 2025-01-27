from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import logging
from .primary_tools import embeddings_tool, generation_tool, pdf_analysis_tool, list_available_documents

# Configurar logger
logger = logging.getLogger('agent_one')
logger.setLevel(logging.INFO)
console_formatter = logging.Formatter('(agent_one) %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.handlers = []
logger.addHandler(console_handler)
logger.propagate = True

class SimpleAgent:
    def __init__(self, user_id: str = "default_user", conversation_id: str = "default_conversation"):
        self.llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
        self.user_id = user_id
        self.conversation_id = conversation_id

        # Definir el prompt base
        self.base_prompt = PromptTemplate(
            input_variables=["query"],
            template="""Eres un asistente técnico especializado en Python, ciencia de datos y machine learning. \
                Ayuda al usuario respondiendo de forma clara, con pasos prácticos y ejemplos relevantes si aplica. \
                Consulta: {query}"""
        )        
        
        self.classification_prompt = PromptTemplate(
            input_variables=["query", "documents"],
            template="""Eres un asistente técnico encargado de decidir qué herramienta es más adecuada \
                para responder a una consulta técnica, siguiendo el orden de prioridad indicado. Aquí están las herramientas disponibles: 
                - Biblioteca de vectores: Busca información en documentos de referencia, tus documentos son: {documents}.
                - Generador de texto: Genera explicaciones detalladas o contenido técnico.
                - Análisis de PDFs: Procesa y analiza documentos PDF.
                
                Consulta: {query}
                
                Devuelve una de las siguientes opciones, sin explicaciones extra: 'embeddings_tool', 'generation_tool', 'pdf_analysis_tool', 'llm'."""
        )
        
    def classify_tool(self, query: str) -> str:
        """
        Usa el modelo LLM para clasificar la consulta y determinar qué herramienta utilizar.
        """
        docs = list_available_documents()
        if 'error' in docs:
            logger.error(f"Error: {docs['error']}")
        else:
            logger.info(f"Encontrados {docs['total_documents']} documentos")
        try:
            classification_query = self.classification_prompt.format(query=query, documents=docs)
            response = self.llm.invoke(classification_query).content.strip()
            return response.lower()
        except Exception as e:
            logger.error(f"Error clasificando la herramienta: {str(e)}")
            return "llm"  

    def handle_query(self, query: str) -> str:
        """
        Maneja una consulta llamando directamente a las herramientas según el tipo de consulta.
        """
        logger.info("=== Iniciando procesamiento de consulta ===")
        try:
            # Validación básica de la consulta
            query = query.strip()
            if len(query) < 3:
                raise ValueError("La consulta es demasiado corta. Por favor, proporcione más detalles.")

            # Clasificar la consulta para seleccionar la herramienta adecuada
            selected_tool = self.classify_tool(query)
            logger.info(f"Herramienta seleccionada: {selected_tool}")

            # Validar y ejecutar la herramienta correspondiente
            if selected_tool == "embeddings_tool":
                logger.info("Usando biblioteca de vectores")
                response = embeddings_tool(query)

            elif selected_tool == "generation_tool":
                logger.info("Usando generación de texto")
                response = generation_tool(query)

            elif selected_tool == "pdf_analysis_tool":
                logger.info("Usando análisis de PDFs")
                pdf_directory = "path_to_pdf_directory"
                if not os.path.exists(pdf_directory) or not os.listdir(pdf_directory):
                    return "No hay documentos PDF disponibles para analizar."
                response = pdf_analysis_tool(query)

            else:
                logger.info("Usando LLM directamente")
                formatted_prompt = self.base_prompt.format(query=query)
                response = self.llm.invoke(formatted_prompt).content.strip()

            return response

        except Exception as e:
            logger.error(f"Error procesando la consulta: {str(e)}")
            return f"Error procesando la consulta: {str(e)}"

