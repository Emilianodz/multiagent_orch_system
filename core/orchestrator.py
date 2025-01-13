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

    def preprocess_query(self, query: str, conversation_id: str) -> str:
        """
        Preprocesa la consulta para generar un input refinado que pueda ser enviado al router.
        """
        query = query.strip()
        if len(query) < 3:
            raise ValueError("La consulta es demasiado corta. Por favor, proporcione más detalles.")

        # Obtener historial de conversación formateado
        context = self.conversation_manager.get_formatted_conversation(conversation_id)

        input_for_openai = (
            f"Historial de la conversación:\n{context}\n\n"
            f"Consulta actual:\n{query}\n\n"
            "Genera una consulta refinada y específica para ser clasificada por un sistema de enrutamiento. "
            "La consulta debe ser concisa y contener únicamente información necesaria para la clasificación técnica:"
        )

        # Generar la consulta refinada
        refined_query = self.llm.invoke(input_for_openai).content.strip()
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
            if not isinstance(router_response, dict) or "response" not in router_response:
                return f"Error en el router: Formato de respuesta inválido."

            # Extraer datos del router
            router_data = router_response.get("response", {})
            module = router_data.get("module", "desconocido")
            response = router_data.get("response", "Sin respuesta proporcionada.")
            conversation_id = router_response.get("conversation_id", "Sin ID de conversación.")
            optional_id = router_response.get("optional_id", "Sin ID opcional.")

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
        Maneja una consulta completa, incluyendo la orquestación entre agentes y herramientas.
        """
        print("\n=== Iniciando procesamiento de consulta en el orquestador ===")
        print(f"ID de conversación: {conversation_id}")

        try:
            # Recuperar o inicializar la conversación
            self.conversation_manager.get_conversation(conversation_id)

            # Preprocesar la consulta
            refined_query = self.preprocess_query(query, conversation_id)
            print(f"Consulta refinada: {refined_query}")

            # Enviar la consulta al router
            router_response = route_query_with_langchain(refined_query)
            print(f"Respuesta del router: {router_response}")

            if not isinstance(router_response, dict):
                raise ValueError(f"Respuesta del router inválida: {router_response}")

            # Manejar la respuesta del router y crear contexto
            context = self.handle_router_response(query, router_response, conversation_id)
            print("Contexto generado correctamente")

            # Agregar la consulta original al historial
            self.conversation_manager.add_message(conversation_id, "user", query)

            # Crear el prompt para el modelo
            prompt_template = PromptTemplate(
                input_variables=["query"],
                template=(
                    "Eres un agente orquestador con conocimiento especializado en sistemas operativos Linux, análisis de datos en Python "
                    "y tecnologías generales. Tu tarea es analizar la consulta proporcionada y decidir entre:\n\n"
                    "1. Responder directamente, si tienes suficiente información.\n"
                    "2. Delegar a un agente especializado si la consulta no está dentro de tu dominio o requiere análisis avanzado.\n\n"
                    "Instrucciones:\n"
                    "- Si la consulta está relacionada con sistemas operativos Linux (comandos, configuraciones, arquitecturas de servidores), responde directamente.\n"
                    "- Si la consulta está relacionada con Python para análisis de datos (bibliotecas, algoritmos o prácticas específicas), rútala al 'Agent_One'.\n"
                    "- Si la consulta es sobre múltiples lenguajes de programación o tecnologías en general, rútala al 'Agent_Two'.\n\n"
                    "Formato de respuesta esperado:\n"
                    "1. Para responder directamente: Proporciona una respuesta clara y completa.\n"
                    "2. Para delegar: Escribe únicamente 'Enviar a [Nombre del Agente]'.\n\n"
                    "Consulta:\n"
                    "{query}\n\n"
                    "Respuesta:"
                )
            )
            prompt = prompt_template.format(query=context)
            print("Prompt generado correctamente")

            # Obtener la respuesta del modelo
            response = self.llm.invoke(prompt)
            print("Respuesta del modelo obtenida")

            # Guardar la respuesta final en el historial
            final_response = response.content.strip()
            self.conversation_manager.add_message(conversation_id, "system", final_response)
            print("guardado en el historial")
            
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
            print("log creado")
            return final_response


            
        except Exception as e:
            print(f"Error en handle_query: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return f"Error procesando la consulta en el orquestador: {str(e)}"
