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
            template="""Eres un asistente técnico especializado en herramientas y lenguajes de programación. \
                Tu objetivo es proporcionar respuestas claras, detalladas y útiles que ayuden al usuario a resolver \
                problemas técnicos, comprender conceptos o tomar decisiones informadas. Estructura tus respuestas \
                con pasos concretos, ejemplos prácticos o detalles relevantes siempre que sea posible.
                Consulta: {query}"""
        )         
        
        self.classification_prompt = PromptTemplate(
            input_variables=["query", "documents"],
            template="""Eres un asistente técnico encargado de decidir qué herramienta es más adecuada \
                para responder a una consulta técnica. Aquí están las herramientas disponibles: 
                - Biblioteca de vectores: Busca información en documentacion de referencia, tus documentos son: {documents}.
                - Generador de texto: Genera explicaciones detalladas o contenido técnico.
                - Análisis de PDFs: Procesa y analiza documentos PDF.
                
                Consulta: {query}
                
                Devuelve una de las siguientes opciones, sin explicaciones extra: 'embeddings_tool', 'generation_tool', 'pdf_analysis_tool', 'llm'."""
        )
        
    def classify_tool(self, query: str) -> str:
        """
        Usa el modelo LLM para clasificar la consulta y determinar qué herramienta utilizar.
        """
        classification_prompt = PromptTemplate(
            input_variables=["query", "documents"],
            template="""Eres un clasificador que debe decidir qué herramienta usar para una consulta, siguiendo el orden de prioridad indicado.
            
            Las herramientas disponibles son:
            - embeddings_tool: Para buscar en documentos de referencia
            - generation_tool: Para generar explicaciones detalladas
            - pdf_analysis_tool: Para analizar PDFs
            - llm: Para respuestas generales
            
            Documentos disponibles: {documents}
            
            Consulta: {query}
            
            IMPORTANTE: Responde ÚNICAMENTE con una de estas palabras exactas:
            'embeddings_tool', 'generation_tool', 'pdf_analysis_tool', 'llm'"""
        )
        
        docs = list_available_documents()
        try:
            classification_query = classification_prompt.format(
                query=query, 
                documents=docs.get('documents', [])
            )
            response = self.llm.invoke(classification_query).content.strip().lower()
            
            # Validar que la respuesta sea una de las opciones válidas
            valid_tools = {'embeddings_tool', 'generation_tool', 'pdf_analysis_tool', 'llm'}
            if response not in valid_tools:
                print(f"Respuesta inválida del clasificador: {response}")
                return 'llm'  # valor por defecto
                
            return response
            
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

