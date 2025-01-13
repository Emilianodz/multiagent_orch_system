from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os
import json

# Ruta de la base de datos
DB_PATH = os.path.join("db", "conversations.json")

# Crear un adaptador personalizado para escribir JSON con indentación
class IndentedJSONStorage(JSONStorage):
    def write(self, data):
        """
        Escribe los datos en el archivo con formato JSON indentado.
        """
        with open(self._handle.name, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)  # Formatear con indentación
            f.write("\n")  # Agregar un salto de línea al final del archivo

# Usar TinyDB con el adaptador personalizado
db = TinyDB(DB_PATH, storage=CachingMiddleware(IndentedJSONStorage))

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
