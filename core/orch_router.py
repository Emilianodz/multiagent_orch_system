import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from .agents.agent_one.primary_tools import embeddings_tool, generation_tool, pdf_analysis_tool
from .agents.agent_one.agent_core import SimpleAgent as AgentOne
from .agents.agent_two.agent_core import SimpleAgent as AgentTwo
import os

# Configurar logging
logger = logging.getLogger('router')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('(router) %(message)s')

# Configurar handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Configurar el modelo LLM
llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

# Prompt optimizado para clasificación directa
classification_prompt = PromptTemplate(
    input_variables=["query"],
    template="""Clasifica estrictamente la consulta en una categoría usando solo estos criterios:

1. **embeddings**: Búsqueda en documentos técnicos sobre Linux. Ej: "Comandos para administrar servicios en systemd"
2. **agent_one**: Programación Python avanzada, ciencia de datos. Ej: "Cómo optimizar un modelo de ML con PyTorch"
3. **agent_two**: Automatización con Bash, Git, MySQL. Ej: "Script para backups automáticos en bash"
4. **generation**: Generación de contenido técnico general. Ej: "Explica los principios de la criptografía"
5. **pdf**: Análisis específico de PDFs. Ej: "Extrae tablas de este manual técnico en PDF"

Consulta: {query}

Respuesta (solo el nombre de la categoría en minúsculas):"""
)

classification_chain = classification_prompt | llm

def dispatch_category(category: str, query: str) -> dict:
    """Ejecuta la lógica para la categoría clasificada."""
    logger.info(f"Iniciando dispatch para categoría: {category}")
    try:
        if category == "embeddings":
            logger.info("Ejecutando herramienta de embeddings")
            print(f"(router) Ejecutando herramienta de embeddings")
            return {"module": "embeddings", "response": embeddings_tool.run(query)}
        
        elif category == "generation":
            logger.info("Ejecutando herramienta de generación")
            print(f"(router) Ejecutando herramienta de generación")
            return {"module": "generation", "response": generation_tool.run(query)}
        
        elif category == "pdf":
            logger.info("Ejecutando herramienta de análisis PDF")
            print(f"(router) Ejecutando herramienta de análisis PDF")
            return {"module": "pdf", "response": pdf_analysis_tool.run(query)}
        
        elif category == "agent_one":
            logger.info("Inicializando Agent One")
            print(f"(router) Inicializando Agent One")
            agent = AgentOne()
            return {"module": "agent_one", "response": agent.handle_query(query)}
        
        elif category == "agent_two":
            logger.info("Inicializando Agent Two")
            print(f"(router) Inicializando Agent Two")
            agent = AgentTwo()
            return {"module": "agent_two", "response": agent.handle_query(query)}
        
        else:
            logger.error(f"Categoría no reconocida: {category}")
            return {"error": f"Categoría '{category}' no reconocida"}

    except Exception as e:
        logger.error(f"ERROR en dispatch_category: {str(e)}")
        return {"error": f"Error en {category}: {str(e)}"}


def route_query_with_langchain(query: str, user_id: str = None, **kwargs) -> dict:
    """Clasificación y enrutamiento directo sin contexto adicional."""
    logger.info(f"Iniciando procesamiento de query. User ID: {user_id}")
    logger.info(f"Query recibida: {query}")
    print(f"(router) Procesando query para usuario: {user_id}")
    
    try:
        # Clasificación precisa
        logger.info("Iniciando clasificación de la query")
        classification = classification_chain.invoke({"query": query.strip()})
        category = classification.content.strip().lower()
        logger.info(f"Categoría clasificada: {category}")
        
        # Validación estricta
        valid_categories = {"embeddings", "generation", "pdf", "agent_one", "agent_two"}
        
        if category not in valid_categories:
            logger.error(f"Categoría inválida detectada: {category}")
            return {
                "error": f"Clasificación inválida: '{category}'",
                "valid_categories": list(valid_categories)
            }
        
        logger.info("Enviando query a dispatch_category")
        result = dispatch_category(category, query.strip())
        logger.info("Proceso completado exitosamente")
        return result

    except Exception as e:
        logger.error(f"ERROR CRÍTICO en el router: {str(e)}")
        return {"error": f"Error crítico en el router: {str(e)}"}