from langchain_openai import ChatOpenAI
import os

# Configurar el modelo LLM
llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

def handle_generation(query: str) -> str:
    """
    Actúa como un motor de búsqueda simulado generando texto relacionado con la consulta del usuario.

    Args:
        query (str): La consulta proporcionada por el usuario.

    Returns:
        str: Una respuesta generada basada en la consulta.
    """
    prompt = (
        f"Eres un motor de búsqueda simulado. "
        f"Analiza la consulta del usuario y proporciona una explicación detallada basada en ella.\n\n"
        f"Consulta: {query}"
    )
    response = llm.invoke(prompt)
    return response.content.strip()


# ============================
# EJECUCIÓN AUTOMÁTICA
# ============================
if __name__ == "__main__":
    print("=== Motor de Búsqueda Simulado ===")
    
    # Prueba básica
    consulta = input("Introduce tu consulta para el motor de búsqueda: ").strip()
    if consulta:
        print("\nGenerando respuesta...")
        respuesta = handle_generation(consulta)
        print(f"\nRespuesta generada:\n{respuesta}")
    else:
        print("No se proporcionó ninguna consulta.")
