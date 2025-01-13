from rest_framework.decorators import api_view
from rest_framework.response import Response
from .orchestrator import OrchestratorAgent  # Importar el orquestador
from .agents.agent_one.agent_core import SimpleAgent as AgentOne  # Importar el Agente 1
from .agents.agent_two.agent_core import SimpleAgent as AgentTwo  # Importar el Agente 2
from .orch_router import route_query_with_langchain  # Importar el Router

@api_view(['POST'])
def agent_view(request):
    """
    Endpoint para manejar consultas usando el orquestador.
    """
    try:
        # Obtener datos de la solicitud
        query = request.data.get('query')
        optional_id = request.data.get('optional_id')
        conversation_id = request.data.get('conversation_id')

        # Validar campos obligatorios
        if not query or not conversation_id:
            return Response({"error": "Faltan campos obligatorios: 'query' y 'conversation_id'"}, status=400)

        # Crear instancia del orquestador
        agent = OrchestratorAgent(user_id=optional_id or "default_user")

        # Procesar la consulta usando el orquestador
        response = agent.handle_query(query=query, conversation_id=conversation_id)

        return Response({
            "response": response,
            "conversation_id": conversation_id,
            "optional_id": optional_id
        })
    except Exception as e:
        return Response({
            "error": f"Error en el procesamiento: {str(e)}",
            "conversation_id": conversation_id if 'conversation_id' in locals() else None,
            "optional_id": optional_id if 'optional_id' in locals() else None
        }, status=500)


@api_view(['POST'])
def router_view(request):
    """
    Endpoint para interactuar directamente con el router.
    """
    try:
        # Obtener datos de la solicitud
        query = request.data.get('query')
        optional_id = request.data.get('optional_id')
        conversation_id = request.data.get('conversation_id')

        # Validar campos obligatorios
        if not query:
            return Response({"error": "Faltan campos obligatorios: 'query'"}, status=400)

        # Procesar la consulta usando el router
        response = route_query_with_langchain(query=query, user_id=optional_id or "default_user", conversation_id=conversation_id or "default_conv")

        return Response({
            "response": response,
            "conversation_id": conversation_id,
            "optional_id": optional_id
        })
    except Exception as e:
        return Response({
            "error": f"Error en el procesamiento del router: {str(e)}",
            "conversation_id": conversation_id if 'conversation_id' in locals() else None,
            "optional_id": optional_id if 'optional_id' in locals() else None
        }, status=500)


@api_view(['POST'])
def agent_one_view(request):
    """
    Endpoint para interactuar directamente con el Agente 1.
    """
    try:
        # Obtener datos de la solicitud
        query = request.data.get('query')
        optional_id = request.data.get('optional_id')
        conversation_id = request.data.get('conversation_id')

        # Validar campos obligatorios
        if not query or not conversation_id:
            return Response({"error": "Faltan campos obligatorios: 'query' y 'conversation_id'"}, status=400)

        # Crear instancia del Agente 1
        agent = AgentOne(user_id=optional_id or "default_user")

        # Procesar la consulta usando el agente
        response = agent.handle_query(query=query, conversation_id=conversation_id)

        return Response({
            "response": response,
            "conversation_id": conversation_id,
            "optional_id": optional_id
        })
    except Exception as e:
        return Response({
            "error": f"Error en el procesamiento del Agente 1: {str(e)}",
            "conversation_id": conversation_id if 'conversation_id' in locals() else None,
            "optional_id": optional_id if 'optional_id' in locals() else None
        }, status=500)


@api_view(['POST'])
def agent_two_view(request):
    """
    Endpoint para interactuar directamente con el Agente 2.
    """
    try:
        # Obtener datos de la solicitud
        query = request.data.get('query')
        optional_id = request.data.get('optional_id')
        conversation_id = request.data.get('conversation_id')

        # Validar campos obligatorios
        if not query or not conversation_id:
            return Response({"error": "Faltan campos obligatorios: 'query' y 'conversation_id'"}, status=400)

        # Crear instancia del Agente 2
        agent = AgentTwo(user_id=optional_id or "default_user")

        # Procesar la consulta usando el agente
        response = agent.handle_query(query=query, conversation_id=conversation_id)

        return Response({
            "response": response,
            "conversation_id": conversation_id,
            "optional_id": optional_id
        })
    except Exception as e:
        return Response({
            "error": f"Error en el procesamiento del Agente 2: {str(e)}",
            "conversation_id": conversation_id if 'conversation_id' in locals() else None,
            "optional_id": optional_id if 'optional_id' in locals() else None
        }, status=500)


@api_view(['GET'])
def health_check_view(request):
    """
    Endpoint para verificar el estado del sistema.
    """
    return Response({
        "status": "OK",
        "message": "The service is running"
    }, status=200)

"""
class AgentAPIView(APIView):
    def post(self, request):
        try:
            query = request.data.get('query')
            if not query:
                return Response({"error": "No query provided"}, status=400)
            
            response = generate_response(query)
            return Response({"response": response})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
"""