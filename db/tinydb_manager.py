from tinydb import TinyDB, Query
import os

# Configurar el archivo de base de datos
DB_PATH = os.path.join("db", "conversations.json")
db = TinyDB(DB_PATH)

class ConversationManager:
    def __init__(self):
        self.db = db
        self.query = Query()


    def add_message(self, conversation_id, sender, message):
        """
        Agrega un mensaje a una conversación específica.
        Las respuestas del sistema no incluirán duplicados.
        """
        conversation = self.get_conversation(conversation_id)

        if sender == "system":
            # No agregar respuestas duplicadas del sistema
            existing_responses = [msg["message"] for msg in conversation["messages"] if msg["sender"] == "system"]
            if message in existing_responses:
                return

        conversation["messages"].append({"sender": sender, "message": message})
        self.db.update(conversation, self.query.conversation_id == conversation_id)

    def get_conversation(self, conversation_id):
        """
        Recupera una conversación completa por su ID, sin formatear.
        """
        conversation = self.db.search(self.query.conversation_id == conversation_id)
        if conversation:
            return conversation[0]  
        else:
            # Si no existe, crear una nueva conversación
            new_conversation = {"conversation_id": conversation_id, "messages": []}
            self.db.insert(new_conversation)
            return new_conversation

    def get_formatted_conversation(self, conversation_id):
        """
        Devuelve un historial formateado como string.
        """
        # Obtener la conversación sin formatear
        conversation = self.get_conversation(conversation_id)
        
        if not conversation or "messages" not in conversation:
            return "Sin historial previo."

        # Formatear el historial de mensajes
        return "\n".join([f"{msg['sender']}: {msg['message']}" for msg in conversation["messages"]])