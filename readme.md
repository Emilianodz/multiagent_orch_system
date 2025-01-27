# Agente Virtual Multiagente para Procesamiento de Consultas Técnicas

## Descripción
Este proyecto implementa una arquitectura multiagente especializada en el procesamiento y respuesta de consultas técnicas, utilizando una combinación de agentes especializados y una biblioteca de vectores para la recuperación de información. El sistema está diseñado para manejar consultas complejas relacionadas con documentación técnica, proporcionando respuestas precisas y contextualizadas basadas en documentos de referencia almacenados.

La arquitectura multiagente permite:
- Procesamiento distribuido de consultas mediante agentes especializados
- Recuperación eficiente de información utilizando búsqueda vectorial
- Mantenimiento de contexto conversacional entre interacciones
- Generación de respuestas coherentes y técnicamente precisas
- Integración con sistemas externos mediante una API REST

## Características
- Sistema de procesamiento de consultas basado en múltiples agentes especializados
- Búsqueda semántica avanzada utilizando embeddings y similitud vectorial
- Integración con modelos de lenguaje de OpenAI para procesamiento de lenguaje natural
- Implementación de grafos para modelado de decisiones y flujos de trabajo
- Sistema de memoria conversacional para mantener contexto entre interacciones
- Capacidad de procesamiento de documentos en múltiples formatos
- API REST para fácil integración con sistemas externos
- Sistema de logging detallado para monitoreo y debugging
- Arquitectura modular y extensible para añadir nuevas funcionalidades
- Gestión eficiente de recursos mediante procesamiento asíncrono
- Soporte para múltiples conversaciones simultáneas

## Arquitectura del Proyecto
El proyecto implementa una arquitectura modular basada en múltiples agentes:

- **core**: Contiene la lógica del orquestador principal y herramientas compartidas
    - orchestrator_agent: Gestiona y coordina las interacciones entre los diferentes agentes
    - orch_router: Analiza y dirige las consultas al agente más apropiado

    - Herramientas especializadas:
            - vector_orch_library: Maneja la biblioteca de vectores principal
        - pdf_orch_tool: Procesamiento de documentos PDF
        - generation_orch_tool: Generación de respuestas, ejemplo a modificar para busqueda o generación espcifica en base a API de terceros
        - primary_orch_tools: Cordinacion de uso de herramientas
    - log_control: Sistema de logging centralizado
    - balance_control: Gestión de carga y recursos

- **agents**: Contiene los agentes especializados
    - agent_1: Primer agente especializado
        - agent_core: Lógica principal del agente
        - Herramientas específicas: pdf_tool, generation_tool, vector_library
    - agent_2: Segundo agente especializado
        - agent_core: Lógica principal del agente
        - Herramientas específicas: pdf_tool, generation_tool, vector_library

- **db**: Sistema de almacenamiento con TinyDB
    - tiny_db: Gestión de la base de datos
    - conversations: Almacenamiento del historial de conversaciones

- **api_project**: Configuración y gestión de Django
    - urls: Enrutamiento de la API
    - settings: Configuración del proyecto
    - wsgi/asgi: Interfaces de servidor web

## Estructura del Proyecto
```
Proyecto
├── api_project
│   ├── __init__.py
│   ├── settings.py
│   ├── asgi.py
│   ├── urls.py
│   ├── wsgi.py
│   └── # Administración base de Django, no relevante en esta etapa
├── core
│   ├── migrations/
│   ├── documents/ # Carpeta de documentos para cada biblioteca
│   ├── storage/ # Vectores de cada biblioteca (3 bibliotecas)
│   ├── admin.py
│   ├── apps.py
│   ├── orchestrator_agent.py
│   ├── orch_router.py
│   ├── pdf_orch_tool.py
│   ├── generation_orch_tool.py
│   ├── vector_orch_library.py
│   ├── primary_orch_tools.py # Lógica del llamado a herramientas
│   ├── log_control.py
│   ├── urls.py
│   ├── views.py
│   └── balance_control.py
├── agents
│   ├── agent_1
│   │   ├── agent_core.py
│   │   ├── pdf_tool.py
│   │   ├── generation_tool.py
│   │   ├── vector_library.py
│   │   └── primary_tools.py
│   └── agent_2
│       ├── agent_core.py
│       ├── pdf_tool.py
│       ├── generation_tool.py
│       ├── vector_library.py
│       └── primary_tools.py
├── commandos.py
└── db
    ├── tiny_db.py
    └── conversations.json
```

## Instalación

### Prerrequisitos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. Clona el repositorio:
```bash
git clone github link
cd multiagent_orch
```

2. Crea y activa un entorno virtual:
```bash
python -m venv venv
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
   - Crea un archivo `.env` en el directorio raíz
   - Añade las siguientes variables:
```plaintext
OPENAI_API_KEY=tu_clave_api_de_openai
DJANGO_SECRET_KEY=tu_clave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Prepara la estructura de directorios:
```bash
mkdir -p core/documents
mkdir -p core/storage
```

6. Realiza las migraciones de Django:
```bash
python manage.py migrate
```

7. Crea un superusuario (opcional):
```bash
python manage.py createsuperuser
```

## Uso

### Configuración Inicial

1. **Preparación de Documentos**
   - Coloca tus documentos técnicos de referencia en la carpeta `core/documents/`
   - Formatos soportados: PDF, TXT, DOCX
   - Organiza los documentos en subcarpetas según la biblioteca correspondiente

2. **Generación de Embeddings y visor de logs**
   Utiliza el script de comandos para inicializar las bibliotecas de vectores:
   ```bash
   # Inicializar todas las bibliotecas
   python commands.py initialize_vectors all

   # Inicializar bibliotecas específicas
   python commands.py initialize_vectors orchestrator  # Solo orquestador
   python commands.py initialize_vectors agent_one     # Solo Agente 1
   python commands.py initialize_vectors agent_two     # Solo Agente 2
   ```

3. **Visor de logs**
   Utiliza el script de comandos para abrir el visor de logs:
   ```bash
   python commands.py logs
   ```

   Para ver la ayuda y lista de comandos disponibles:
   ```bash
   python commands.py help
   ```

### Iniciar el Servidor
```bash
python manage.py runserver
```

### Endpoints Disponibles

#### Orquestador Principal
- **POST /api/agent/**
  - Maneja consultas usando el orquestador principal
  ```json
  {
    "query": "Tu consulta aquí",
    "optional_id": "id_usuario",
    "conversation_id": "id_conversacion"
  }
  ```

#### Router
- **POST /api/router/**
  - Interactúa directamente con el router de consultas
  ```json
  {
    "query": "Tu consulta aquí",
    "optional_id": "id_usuario",
    "conversation_id": "id_conversacion"
  }
  ```

#### Agentes Específicos
- **POST /api/agent-one/**
  - Interactúa directamente con el Agente 1
  ```json
  {
    "query": "Tu consulta aquí",
    "optional_id": "id_usuario",
    "conversation_id": "id_conversacion"
  }
  ```

- **POST /api/agent-two/**
  - Interactúa directamente con el Agente 2
  ```json
  {
    "query": "Tu consulta aquí",
    "optional_id": "id_usuario",
    "conversation_id": "id_conversacion"
  }
  ```

#### Health Check
- **GET /api/health/**
  - Verifica el estado del sistema
  - Respuesta:
  ```json
  {
    "status": "OK",
    "message": "El servicio está funcionando correctamente."
  }
  ```

#### Respuestas de Error
En caso de error, los endpoints responderán con:
```json
{
    "error": "Descripción del error",
    "conversation_id": "id_conversacion",
    "optional_id": "id_usuario"
}
```

## Flujo de Trabajo

### Procesamiento de Consultas
1. **Recepción de Consulta**
   - La API recibe la consulta a través del endpoint principal
   - Se valida la consulta y se crea/recupera el ID de conversación
   - El orchestrator_agent mantiene el contexto y memoria de la conversación

2. **Orquestación**
   - El orchestrator_agent recibe la consulta
   - Analiza el contenido y contexto de la conversación
   - Decide si procesa directamente la consulta o la envía al router
   - Puede modificar la query original para obtener resultados más específicos

3. **Enrutamiento (si se utiliza)**
   - El orch_router evalúa la consulta y decide entre:
     - Usar agentes especializados
     - Utilizar herramientas del orquestador
     - Combinar múltiples recursos
   - El uso de herramientas es opcional tanto para el router como para los agentes
   - Reenvía todas las respuestas al orquestador para evaluación

4. **Procesamiento**
   - Los agentes o herramientas procesan la consulta según sus capacidades
   - El uso de herramientas (pdf_tool, generation_tool, etc.) es opcional
   - Cada componente puede utilizar su propia biblioteca de vectores si es necesario

5. **Respuesta Final**
   - El orchestrator_agent evalúa todas las respuestas recibidas
   - Selecciona la mejor respuesta o combina múltiples respuestas
   - Puede iniciar nuevas iteraciones si la consulta original no se resolvió satisfactoriamente
   - Aplica post-procesamiento según sea necesario
   - Mantiene y actualiza el contexto de la conversación
   - Envía la respuesta final al usuario

### Gestión de Recursos
- El sistema mantiene un registro continuo a través de log_control
- El orquestador es el único componente que mantiene el contexto completo de la conversación
