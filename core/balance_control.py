class BalanceManager:
    """
    Clase básica para manejar el balanceo entre múltiples respuestas.
    """

    def __init__(self):
        self.criteria_weights = {
            "confidence": 1.0,  # Peso para la confianza en la respuesta
            "relevance": 1.0,  # Peso para la relevancia
            "time": 0.5        # Peso para el tiempo de respuesta (penaliza respuestas lentas)
        }

    def evaluate_responses(self, responses: list) -> dict:
        """
        Evalúa las respuestas según los criterios establecidos y devuelve la mejor.

        Args:
            responses (list): Lista de respuestas en formato:
                [
                    {"response": "Texto de respuesta", "confidence": 0.9, "relevance": 0.8, "time": 120},
                    ...
                ]

        Returns:
            dict: La mejor respuesta según la evaluación.
        """
        if not responses:
            return {"error": "No hay respuestas para evaluar."}

        # Asignar un puntaje total a cada respuesta según los criterios y pesos
        for response in responses:
            response["score"] = (
                response.get("confidence", 0) * self.criteria_weights["confidence"] +
                response.get("relevance", 0) * self.criteria_weights["relevance"] -
                response.get("time", 0) * self.criteria_weights["time"]
            )

        # Seleccionar la respuesta con el puntaje más alto
        best_response = max(responses, key=lambda r: r["score"])

        return best_response

    def adjust_criteria_weights(self, confidence_weight=1.0, relevance_weight=1.0, time_weight=0.5):
        """
        Ajusta los pesos de los criterios para el balanceador.

        Args:
            confidence_weight (float): Peso para la confianza.
            relevance_weight (float): Peso para la relevancia.
            time_weight (float): Peso para el tiempo de respuesta.
        """
        self.criteria_weights["confidence"] = confidence_weight
        self.criteria_weights["relevance"] = relevance_weight
        self.criteria_weights["time"] = time_weight
