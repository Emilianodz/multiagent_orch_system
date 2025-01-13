from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from .primary_tools import embeddings_tool, generation_tool, pdf_analysis_tool, list_available_documents

class SimpleAgent:
    def __init__(self, user_id):
        self.llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
        self.user_id = user_id

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
            print(f"Error: {docs['error']}")
        else:
            print(f"Encontrados {docs['total_documents']} documentos")
        try:
            classification_query = self.classification_prompt.format(query=query, documents=docs)
            response = self.llm.invoke(classification_query).content.strip()
            return response.lower()
        except Exception as e:
            print(f"Error clasificando la herramienta: {str(e)}")
            return "llm"  

    def handle_query(self, query: str, conversation_id: str) -> str:
        """
        Maneja una consulta llamando directamente a las herramientas según el tipo de consulta.
        """
        print("\n=== Iniciando procesamiento de consulta en Agent_Two ===")
        try:
            # Validación básica de la consulta
            query = query.strip()
            if len(query) < 3:
                raise ValueError("La consulta es demasiado corta. Por favor, proporcione más detalles.")

            # Clasificar la consulta para seleccionar la herramienta adecuada
            selected_tool = self.classify_tool(query)
            print(f"Herramienta seleccionada: {selected_tool}")

            # Validar y ejecutar la herramienta correspondiente
            if selected_tool == "embeddings_tool":
                print("Usando la herramienta de biblioteca de vectores...")
                response = embeddings_tool(query)

            elif selected_tool == "generation_tool":
                print("Usando la herramienta de generación de texto...")
                response = generation_tool(query)

            elif selected_tool == "pdf_analysis_tool":
                print("Usando la herramienta de análisis de PDFs...")
                
                # Verificar si hay documentos PDF disponibles antes de ejecutar
                pdf_directory = "path_to_pdf_directory"  # Ruta a los PDFs
                if not os.path.exists(pdf_directory) or not os.listdir(pdf_directory):
                    return "No hay documentos PDF disponibles para analizar."
                
                response = pdf_analysis_tool(query)

            else:  # Caso por defecto: usar LLM directamente
                print("Usando LLM directamente...")
                formatted_prompt = self.base_prompt.format(query=query)
                response = self.llm.invoke(formatted_prompt).content.strip()

            return response

        except Exception as e:
            print(f"Error en Agent_Two: {str(e)}")
            return f"Error procesando la consulta en Agent_Two: {str(e)}"

