from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from .agents.agent_one.primary_tools import embeddings_tool, generation_tool, pdf_analysis_tool
from .agents.agent_one.agent_core import SimpleAgent as AgentOne
from .agents.agent_two.agent_core import SimpleAgent as AgentTwo
import os


# Configurar el modelo LLM
llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

# Crear el prompt template para clasificación
classification_prompt = PromptTemplate(
    input_variables=["query"],
    template="""Clasifica la siguiente consulta en una de estas categorías, siguiendo el orden de prioridad indicado:
    
    1. 'embeddings': Utiliza esta categoría para buscar información en documentos mediante búsqueda contextual. 
        Debes usar esta categoría si la consulta está relacionada con documentos o conocimientos específicos que puedan estar en la biblioteca,
        los ocnocimientos actuales es sobre sistemas linux.
    
    2. 'agent_one': Utiliza esta categoría si la consulta requiere análisis avanzado de datos, machine learning, o programación en Python.
        Este agente es ideal para resolver problemas técnicos avanzados en ciencia de datos.

    3. 'agent_two': Utiliza esta categoría si la consulta está relacionada con bash, git, mysql, nodejs.
        Este agente es ideal para automatizaciones y tareas de administración de sistemas.

    4. 'generation': Utiliza esta categoría para generar texto o contenido técnico cuando ninguna otra categoría pueda abordar directamente la consulta.

    5. 'pdf': Utiliza esta categoría para analizar información contenida en documentos PDF. 
        Específicamente para casos donde se mencione explícitamente un PDF o un documento relacionado.

    Consulta: {query}

    Devuelve únicamente uno de los siguientes valores exactos: embeddings, generation, pdf, agent_one, agent_two.
    Categoría:"""
)

# Crear la cadena de clasificación
classification_chain = classification_prompt | llm  # Nueva sintaxis de pipe


def dispatch_category(category: str, query: str, user_id: str, conversation_id: str) -> dict:
    """
    Ejecuta la lógica correspondiente para la categoría clasificada.

    Args:
        category (str): Categoría clasificada.
        query (str): Consulta del usuario.
        user_id (str): ID del usuario.
        conversation_id (str): ID de la conversación.

    Returns:
        dict: Respuesta generada por el módulo o agente correspondiente.
    """
    try:
        if category == "embeddings":
            print("Usando la herramienta de biblioteca de vectores...")
            return {"module": "embeddings", "response": embeddings_tool.run(query)}

        elif category == "generation":
            print("Usando la herramienta de generación de texto...")
            return {"module": "generation", "response": generation_tool.run(query)}

        elif category == "pdf":
            print("Usando la herramienta de análisis de PDFs...")
            return {"module": "pdf", "response": pdf_analysis_tool.run(query)}

        elif category == "agent_one":
            print("Delegando al Agente 1...")
            agent_one = AgentOne(user_id=user_id)
            response = agent_one.handle_query(query, conversation_id)
            return {"module": "agent_one", "response": response}

        elif category == "agent_two":
            print("Delegando al Agente 2...")
            agent_two = AgentTwo(user_id=user_id)
            response = agent_two.handle_query(query, conversation_id)
            return {"module": "agent_two", "response": response}

        else:
            # Categoría no reconocida
            print("Categoría no reconocida.")
            return {"error": "Categoría no válida.", "classification": category}

    except Exception as e:
        print(f"Error en dispatch_category: {str(e)}")
        return {"error": f"Error procesando la categoría: {str(e)}"}


def route_query_with_langchain(query: str, user_id: str = "default_user", conversation_id: str = "default_conv") -> dict:
    """
    Utiliza LangChain para clasificar la consulta y redirigirla al módulo o agente correspondiente.

    Args:
        query (str): La consulta del usuario.
        user_id (str): ID del usuario.
        conversation_id (str): ID de la conversación.

    Returns:
        dict: Respuesta generada por el módulo o agente correspondiente.
    """
    try:
        # Usar la cadena para clasificar
        classification_result = classification_chain.invoke({"query": query.strip()})
        
        # Extraer y limpiar la categoría
        category = classification_result.content.strip().lower()
        category = category.replace("\n", "").replace("\r", "").strip()
        print(f"Categoría clasificada: {category}")

        # Validar categoría
        valid_categories = ["embeddings", "generation", "pdf", "agent_one", "agent_two"]
        if category not in valid_categories:
            print(f"{category}")
            print(f"Respuesta inesperada del clasificador: '{category}'")
            return {
                "error": "Clasificación inválida. Intenta ser más específico.",
                "classification": category
            }

        # Ejecutar lógica según la categoría
        return dispatch_category(category, query, user_id, conversation_id)

    except Exception as e:
        print(f"Error en route_query_with_langchain: {str(e)}")
        return {
            "error": f"Error al procesar la consulta: {str(e)}",
            "classification": None
        }