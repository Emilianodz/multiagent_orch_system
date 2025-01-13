from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from .orch_router import route_query_with_langchain  # Enrutador para delegar tareas a herramientas/agentes
from db.tinydb_manager import ConversationManager
from .log_control import LogManager



class OrchestratorAgent:
    def __init__(self, user_id):
        # Inicialización del modelo LLM
        self.llm = ChatOpenAI(
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.user_id = user_id
        self.conversation_manager = ConversationManager()  # Manejo de conversaciones con TinyDB
        LogManager.start_log_viewer()  # Iniciar el visor de logs
        
        self.refine_query_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""
            f"Historial de la conversación:\n{context}\n\n"
            f"Consulta actual:\n{query}\n\n"
            "Genera una consulta refinada y específica para ser clasificada por un sistema de enrutamiento. "
            "La consulta debe ser concisa y contener únicamente información necesaria para la clasificación técnica:"
            """
        )
        
        self.orchestrator_prompt = PromptTemplate(
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

    def preprocess_query(self, query: str, conversation_id: str) -> str:
        """
        Preprocesa la consulta para generar un input refinado que pueda ser enviado al router.
        """
        query = query.strip()
        if len(query) < 3:
            raise ValueError("La consulta es demasiado corta. Por favor, proporcione más detalles.")

        # Obtener historial de conversación formateado
        context = self.conversation_manager.get_formatted_conversation(conversation_id)


        # Generar la consulta refinada
        refined_query = self.llm.invoke(self.refine_query_prompt.format(query=query, context=context)).content.strip()
        print(f"Consulta refinada: {refined_query}")
        return refined_query

    def handle_router_response(self, query: str, router_response: dict, conversation_id: str) -> str:
        """
        Maneja la respuesta del router y genera el contexto para que el LLM lo procese.

        Args:
            query (str): La consulta original del usuario.
            router_response (dict): Respuesta del router.
            conversation_id (str): ID de la conversación actual.

        Returns:
            str: Contexto detallado generado para la siguiente etapa.
        """
        try:
            # Validar que la respuesta del router contenga la estructura esperada
            if not isinstance(router_response, dict) or "module" not in router_response:
                return f"Error en el router: Formato de respuesta inválido."

            # Extraer datos del router
            module = router_response.get("module", "desconocido")
            response = router_response.get("response", "Sin respuesta proporcionada.")
            conversation_id = conversation_id  # Ya lo tenemos como parámetro
            optional_id = "Sin ID opcional"  # Valor por defecto si no existe

            # Historial de conversación previo
            conversation = self.conversation_manager.get_conversation(conversation_id)
            history = "\n".join(
                [f"{msg['sender']}: {msg['message']}" for msg in conversation.get("messages", [])]
            ) if conversation else "Sin historial previo."

            # Crear un contexto detallado
            full_context = (
                f"Consulta original:\n{query.strip()}\n\n"
                f"Tarea asignada por el router: {module}\n\n"
                f"Respuesta generada por el router:\n{response.strip()}\n\n"
                f"Historial de conversación:\n{history.strip()}\n\n"
                f"Metadata:\n- ID de conversación: {conversation_id}\n- ID opcional: {optional_id}"
            )
            print(f"Contexto generado: {full_context}")
            return full_context

        except Exception as e:
            print(f"Error en handle_router_response: {str(e)}")
            return f"Error procesando la respuesta del router: {str(e)}"

    def handle_query(self, query: str, conversation_id: str) -> str:
        """
        Orquesta el flujo completo esperando únicamente la respuesta final del router
        y enriqueciéndola antes de enviarla al usuario.
        """
        try:
            # Preprocesar la consulta para refinarla
            refined_query = self.preprocess_query(query, conversation_id)

            # Enviar la consulta refinada al router
            router_response = route_query_with_langchain(refined_query)
            print(f"Respuesta del router (tipo {type(router_response)}): {router_response}")

            # Validar que la respuesta sea un diccionario
            if not isinstance(router_response, dict) or "response" not in router_response:
                raise ValueError("Error en el router: Formato de respuesta inválido.")

            # Obtener la respuesta final del router
            agent_response = router_response["response"]
            print(f"Respuesta final recibida del router: {agent_response}")

            # Obtener historial de la conversación para enriquecer la respuesta
            context = self.conversation_manager.get_formatted_conversation(conversation_id)

            # Crear el prompt para enriquecer la respuesta
            prompt = self.orchestrator_prompt.format(
                query=query,
                agent_response=agent_response,
                context=context
            )
            print("Prompt generado correctamente")

            # Obtener la respuesta final del modelo
            response = self.llm.invoke(prompt)
            print("Respuesta enriquecida obtenida del modelo")

            # Guardar la consulta y la respuesta final en el historial
            final_response = response.content.strip()
            self.conversation_manager.add_message(conversation_id, "user", query)
            self.conversation_manager.add_message(conversation_id, "system", final_response)
            print("Respuesta final guardada en el historial")

            # Crear y registrar el log de la interacción
            log_entry = LogManager.create_log_entry(
                user_id=self.user_id,
                conversation_id=conversation_id,
                query=query,
                router_query=refined_query,
                router_response=router_response,
                final_response=final_response
            )
            LogManager.log_interaction(log_entry)
            print("Log creado")

            return final_response

        except Exception as e:
            print(f"Error en handle_query: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"Error procesando la consulta en el orquestador: {str(e)}"

