from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import logging
import traceback
from .orch_router import route_query_with_langchain  # Enrutador para delegar tareas a herramientas/agentes
from db.tinydb_manager import ConversationManager
from .log_control import LogManager
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional

# Configurar logging
logger = logging.getLogger('orchestrator')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('(orchestrator) %(message)s')

# Configurar handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class OrchestratorAgent:
    def __init__(self, user_id):
        try:
            logger.info("=== INICIANDO ORCHESTRATOR AGENT ===")
            logger.info("Inicializando componentes...")
            self.llm = ChatOpenAI(
                temperature=0.7,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            self.user_id = user_id
            self.conversation_manager = ConversationManager()
            
            logger.info("Inicializando grafo de decisiones...")
            self.orchestrator_graph = self._initialize_graph()
            
            logger.info("=== ORCHESTRATOR AGENT INICIADO CON ÉXITO ===")
            
        except Exception as e:
            logger.error(f"Error en inicialización: {str(e)}")
            logger.error(f"Detalles completos del error:\n{traceback.format_exc()}")
            raise

    def _initialize_graph(self):
        """
        Crea el grafo de decisiones del orquestador con un esquema adaptado a los datos de entrada.
        """
        logger.info("Definiendo esquema del estado...")
        class StateSchema(TypedDict):
            query: str
            conversation_id: str
            optional_id: str
            response: str
            refined_query: str
            is_general: bool

        logger.info("Creando grafo con el esquema...")
        graph = StateGraph(StateSchema)
        logger.info("Grafo base creado")

        # Guardamos referencias necesarias
        llm = self.llm
        conversation_manager = self.conversation_manager

        # Definición de prompts
        refine_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=(
                "Como un asistente técnico especializado, tu tarea es refinar y clarificar "
                "la siguiente consulta técnica basándote en el contexto de la conversación.\n\n"
                "Consulta original: {query}\n\n"
                "Contexto de la conversación:\n{context}\n\n"
                "Por favor, reformula la consulta de manera más específica y técnica, "
                "manteniendo la esencia de la pregunta original pero agregando cualquier "
                "detalle relevante del contexto:"
            )
        )

        orchestrator_prompt = PromptTemplate(
            input_variables=["query", "agent_response", "context"],
            template=(
                "Eres un orquestador técnico especializado en Linux, análisis de datos en Python, y tecnologías generales. "
                "Tu tarea es enriquecer la respuesta proporcionada con base en la consulta original y el historial.\n\n"
                "Consulta del usuario:\n{query}\n\n"
                "Respuesta del agente o herramienta seleccionada:\n{agent_response}\n\n"
                "Historial de la conversación:\n{context}\n\n"
                "Genera una respuesta clara, profesional y detallada para el usuario:"
            )
        )

        classification_prompt = PromptTemplate(
            input_variables=["query"],
            template=(
                "Eres un modelo de lenguaje especializado en clasificación de consultas.\n"
                "Tu tarea es evaluar si la consulta siguiente es una pregunta general o técnica.\n\n"
                "Consulta: {query}\n\n"
                "Responde únicamente con 'general' o 'técnica'."
            )
        )

        def classify_query(context):
            logger.info("=== CLASIFICACIÓN DE CONSULTA ===")
            logger.info(f"Consulta original: {context['query']}")
            
            query = context["query"]
            classification = llm.invoke(
                classification_prompt.format(query=query)
            ).content.strip().lower()
            context["is_general"] = classification == "general"
            
            logger.info(f"Clasificación: {classification}")
            return context

        def handle_general_query(context):
            logger.info("=== MANEJANDO CONSULTA GENERAL ===")
            
            conv_history = conversation_manager.get_formatted_conversation(context['conversation_id'])
            response = llm.invoke(
                orchestrator_prompt.format(
                    query=context['query'],
                    agent_response="Esta es una consulta general sobre tecnología.",
                    context=conv_history
                )
            ).content.strip()
            
            context["response"] = response
            logger.info("Respuesta general generada")
            return context

        def refine_and_route_query(context):
            logger.info("=== REFINAMIENTO Y ENRUTAMIENTO ===")
            
            conv_history = conversation_manager.get_formatted_conversation(context['conversation_id'])
            refined_query = llm.invoke(
                refine_prompt.format(
                    query=context['query'],
                    context=conv_history
                )
            ).content.strip()
            context["refined_query"] = refined_query
            
            logger.info(f"Consulta refinada: {refined_query}")
            
            router_response = route_query_with_langchain(refined_query)
            
            final_response = llm.invoke(
                orchestrator_prompt.format(
                    query=context['query'],
                    agent_response=router_response.get("response", "Error en el router"),
                    context=conv_history
                )
            ).content.strip()
            
            context["response"] = final_response
            logger.info("Respuesta técnica generada")
            return context

        logger.info("Agregando nodos al grafo...")
        graph.add_node("Classify Query", classify_query)
        graph.add_node("Handle General Query", handle_general_query)
        graph.add_node("Refine and Route Query", refine_and_route_query)

        logger.info("Definiendo transiciones...")
        graph.add_edge(START, "Classify Query")
        graph.add_conditional_edges(
            "Classify Query",
            lambda x: "Handle General Query" if x["is_general"] else "Refine and Route Query"
        )
        graph.add_edge("Handle General Query", END)
        graph.add_edge("Refine and Route Query", END)

        logger.info("Compilando grafo...")
        workflow = graph.compile()
        logger.info("Grafo compilado exitosamente")
        
        return workflow

    def handle_query(self, query: str, conversation_id: str, optional_id: str = "default_user") -> str:
        """
        Orquesta el flujo completo usando el grafo para decidir si manejar la consulta
        directamente o delegarla al router.
        """
        try:
            logger.info(f"Procesando nueva consulta: {query}")
            
            context = {
                "query": query.strip(),
                "conversation_id": conversation_id,
                "optional_id": optional_id,
                "response": "",
                "refined_query": "",
                "is_general": False
            }

            try:
                result = self.orchestrator_graph.invoke(context)
                logger.info("Grafo ejecutado exitosamente")
            except Exception as graph_error:
                logger.error(f"Error en la ejecución del grafo: {str(graph_error)}")
                raise

            final_response = result["response"]
            
            # Guardar conversación
            self.conversation_manager.add_message(conversation_id, "user", query)
            self.conversation_manager.add_message(conversation_id, "system", final_response)

            # Registrar log
            log_entry = LogManager.create_log_entry(
                user_id=self.user_id,
                conversation_id=conversation_id,
                query=query,
                router_query=result.get("refined_query", ""),
                router_response=result.get("response", ""),
                final_response=final_response
            )
            LogManager.log_interaction(log_entry)
            
            logger.info("Respuesta generada exitosamente")
            return final_response

        except Exception as e:
            logger.error(f"Error en handle_query: {str(e)}")
            logger.error(f"Detalles completos:\n{traceback.format_exc()}")
            return f"Error procesando la consulta en el orquestador: {str(e)}"
