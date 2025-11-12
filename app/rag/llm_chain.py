"""LLM chain configuration and prompt engineering."""
from enum import Enum
from typing import Optional

# langchain imports - compatible with multiple versions
from langchain_core.prompts import PromptTemplate

# for LangChain 1.0+, chains are imported from langchain.chains directly
# LangChain 1.0+ uses a different structure - chains are in langchain.chains
from langchain.chains import ConversationalRetrievalChain, RetrievalQA

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as exc:
    raise ImportError(
        "langchain-google-genai no está instalado. Ejecuta: pip install langchain-google-genai"
    ) from exc

from app.core.config import Settings, load_settings
from app.rag.memory import build_memory, get_memory
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


class PromptType(str, Enum):
    """Available prompt engineering techniques."""
    DEFAULT = "default"  # structured prompt with sections
    FEW_SHOT = "few_shot"  # includes example Q&A pairs
    CHAIN_OF_THOUGHT = "chain_of_thought"  # step-by-step reasoning
    STRUCTURED = "structured"  # highly structured with strict format
    DIRECT = "direct"  # concise and direct answer

# base system prompt used by all prompt types
BASE_SYSTEM_PROMPT = """
Eres un asistente médico especializado en primeros auxilios y medicina general,
entrenado para responder SOLO con la información de las guías médicas proporcionadas (MSF y Cruz Roja).

REGLAS CRÍTICAS:
- Usa ÚNICAMENTE la información proporcionada en el contexto.
- Busca ACTIVAMENTE información relevante en TODO el contexto, incluso si está mezclada con otra información.
- Si encuentras información relevante (aunque sea parcial), úsala para dar una respuesta útil.
- Si el contexto contiene información sobre el tema, incluye TODOS los detalles importantes.
- Solo responde "No tengo suficiente información médica para responder con certeza" si REALMENTE no hay NINGUNA información relevante en el contexto.
- NUNCA inventes, asumas o agregues información que no esté en el contexto.
""".strip()

# default structured prompt template
DEFAULT_TEMPLATE = """
{system_prompt}

<context>
{context}
</context>

Pregunta del usuario: {question}

INSTRUCCIONES:
- Revisa TODO el contexto proporcionado CAREFULMENTE y busca información relevante sobre la pregunta.
- El contexto puede contener información mezclada; busca activamente cualquier mención relacionada con la pregunta.
- Si encuentras información relevante (aunque sea parcial o esté mezclada con otra información), úsala para construir una respuesta útil.
- Proporciona una respuesta COMPLETA y DETALLADA usando SOLO la información del contexto.
- Si hay múltiples pasos o procedimientos en el contexto, inclúyelos TODOS.
- Estructura tu respuesta de forma clara y profesional.
- Solo di "No tengo suficiente información médica" si REALMENTE no encuentras NINGUNA información relevante después de revisar TODO el contexto.

Responde en formato estructurado con las siguientes secciones (incluye todas las que apliquen según el contexto):

**Diagnóstico o Evaluación:**
[Describe cómo identificar o evaluar la condición según el contexto]

**Pasos de Primeros Auxilios:**
[Enumera TODOS los pasos mencionados en el contexto, explicando cada uno claramente]

**Signos de Alarma / Cuándo Buscar Ayuda:**
[Incluye cualquier condición de peligro, signos de alarma o situaciones que requieran atención médica si están en el contexto]

**Recomendaciones o Tratamiento:**
[Describe el tratamiento, cuidados posteriores o recomendaciones si están en el contexto]

**Notas Importantes:**
[Incluye precauciones, contraindicaciones o información adicional relevante del contexto]
""".strip()

# few-shot prompt with example Q&A pairs
FEW_SHOT_TEMPLATE = """
{system_prompt}

<context>
{context}
</context>

Pregunta del usuario: {question}

INSTRUCCIONES:
- Revisa TODO el contexto proporcionado CAREFULMENTE y busca información relevante sobre la pregunta.
- Proporciona una respuesta COMPLETA y DETALLADA usando SOLO la información del contexto.
- Estructura tu respuesta de forma clara y profesional.

EJEMPLOS DE RESPUESTAS CORRECTAS:

Ejemplo 1:
Pregunta: "¿Qué debo hacer si alguien tiene una quemadura?"
Respuesta: **Diagnóstico o Evaluación:** Identifica el grado de la quemadura según el contexto proporcionado.
**Pasos de Primeros Auxilios:** 1. Enfriar la zona con agua fría. 2. Cubrir con gasa estéril. 3. No aplicar cremas ni pomadas.
**Signos de Alarma:** Buscar ayuda médica si la quemadura es extensa o profunda.
**Recomendaciones:** Mantener la zona limpia y protegida.

Ejemplo 2:
Pregunta: "¿Cómo tratar una herida sangrante?"
Respuesta: **Pasos de Primeros Auxilios:** 1. Presionar directamente sobre la herida con gasa estéril. 2. Elevar la extremidad si es posible. 3. Mantener la presión hasta que cese el sangrado.
**Signos de Alarma:** Si el sangrado no cesa después de 10 minutos, buscar ayuda médica inmediatamente.

Ahora responde la pregunta del usuario siguiendo el mismo formato y nivel de detalle que los ejemplos anteriores.
""".strip()

# chain-of-thought prompt with step-by-step reasoning
CHAIN_OF_THOUGHT_TEMPLATE = """
{system_prompt}

<context>
{context}
</context>

Pregunta del usuario: {question}

INSTRUCCIONES:
Responde siguiendo este proceso de razonamiento paso a paso:

PASO 1 - ANÁLISIS DEL CONTEXTO:
Primero, identifica qué información relevante existe en el contexto sobre la pregunta. Menciona específicamente qué partes del contexto son relevantes.

PASO 2 - EVALUACIÓN DE LA INFORMACIÓN:
Analiza la información encontrada. ¿Es completa? ¿Hay información parcial? ¿Qué aspectos cubre y cuáles no?

PASO 3 - CONSTRUCCIÓN DE LA RESPUESTA:
Basándote en el análisis anterior, construye una respuesta estructurada que incluya:
- Diagnóstico o evaluación inicial
- Pasos de primeros auxilios o tratamiento
- Signos de alarma o cuándo buscar ayuda
- Recomendaciones adicionales
- Precauciones importantes

PASO 4 - VERIFICACIÓN:
Verifica que tu respuesta usa SOLO información del contexto y no incluye información inventada.

Ahora ejecuta estos pasos y proporciona tu respuesta completa.
""".strip()

# highly structured prompt with strict format
STRUCTURED_TEMPLATE = """
{system_prompt}

<context>
{context}
</context>

Pregunta del usuario: {question}

INSTRUCCIONES:
Proporciona una respuesta siguiendo EXACTAMENTE este formato. Completa todas las secciones que apliquen según el contexto:

=== DIAGNÓSTICO O EVALUACIÓN ===
[Si el contexto menciona cómo identificar o evaluar la condición, describe el proceso aquí. Si no, escribe "No especificado en el contexto".]

=== PASOS DE PRIMEROS AUXILIOS ===
[Si el contexto menciona pasos específicos, enumera cada uno numerado. Si no, escribe "No especificado en el contexto".]

=== SIGNOS DE ALARMA / CUÁNDO BUSCAR AYUDA ===
[Si el contexto menciona signos de alarma o situaciones de emergencia, listalos aquí. Si no, escribe "No especificado en el contexto".]

=== RECOMENDACIONES O TRATAMIENTO ===
[Si el contexto menciona tratamiento o recomendaciones, descríbelas aquí. Si no, escribe "No especificado en el contexto".]

=== NOTAS IMPORTANTES ===
[Si el contexto menciona precauciones, contraindicaciones o información adicional, inclúyela aquí. Si no, escribe "No especificado en el contexto".]

IMPORTANTE: Usa SOLO información del contexto. Si una sección no tiene información relevante en el contexto, indica "No especificado en el contexto" en lugar de inventar información.
""".strip()

# direct and concise prompt
DIRECT_TEMPLATE = """
{system_prompt}

<context>
{context}
</context>

Pregunta: {question}

Responde de forma directa y concisa usando SOLO la información del contexto proporcionado. 
Incluye los pasos, síntomas, tratamientos o recomendaciones mencionados en el contexto.
Si no encuentras información relevante en el contexto, di "No tengo suficiente información médica para responder con certeza".
""".strip()


def get_llm(model_name: Optional[str] = None, temperature: float = 0.2, settings: Optional[Settings] = None) -> ChatGoogleGenerativeAI:
    """Initialize and return Gemini LLM client."""
    # load settings if not provided
    settings = settings or load_settings()
    # use provided model name or fall back to settings default
    resolved_model = model_name or settings.llm_model_name
    
    # validate that API key is configured
    if not settings.llm_api_key:
        raise RuntimeError(
            "LLM_API_KEY no está configurada. Añádela a tu archivo `.env`.\n"
            "Para Gemini, obtén tu API key en: https://makersuite.google.com/app/apikey"
        )
    
    try:
        # clean up model name if it has the models/ prefix
        model_to_use = resolved_model
        if model_to_use.startswith("models/"):
            model_to_use = model_to_use.replace("models/", "")
        
        # create the Gemini LLM client with specified model and temperature
        # temperature controls randomness: lower = more deterministic, higher = more creative
        llm = ChatGoogleGenerativeAI(
            model=model_to_use,
            temperature=temperature,
            google_api_key=settings.llm_api_key,
        )
        
        return llm
    except Exception as exc:
        # provide helpful error message if initialization fails
        raise RuntimeError(
            f"No se pudo inicializar cliente Gemini. Verifica tu `.env`:\n"
            f"  LLM_API_KEY={'***' + settings.llm_api_key[-4:] if settings.llm_api_key else 'NO CONFIGURADA'}\n"
            f"  LLM_MODEL_NAME={settings.llm_model_name}\n"
            f"Error: {exc}\n\n"
            f"Asegúrate de que:\n"
            f"1. Tu API key de Gemini es válida\n"
            f"2. La API key tiene permisos para usar Gemini\n"
            f"3. El modelo '{resolved_model}' está disponible"
        ) from exc


def get_prompt(prompt_type: PromptType = PromptType.DEFAULT) -> PromptTemplate:
    """Get the configured prompt template for the LLM based on prompt type."""
    # select template based on prompt type
    template_map = {
        PromptType.DEFAULT: DEFAULT_TEMPLATE,
        PromptType.FEW_SHOT: FEW_SHOT_TEMPLATE,
        PromptType.CHAIN_OF_THOUGHT: CHAIN_OF_THOUGHT_TEMPLATE,
        PromptType.STRUCTURED: STRUCTURED_TEMPLATE,
        PromptType.DIRECT: DIRECT_TEMPLATE,
    }
    
    template = template_map.get(prompt_type, DEFAULT_TEMPLATE)
    
    # create a prompt template with context and question as input variables
    # system_prompt is injected as a partial variable (fixed value)
    return PromptTemplate(
        input_variables=["context", "question"],
        template=template,
        partial_variables={"system_prompt": BASE_SYSTEM_PROMPT},
    )


def build_retrieval_qa_chain(
    retriever, 
    model_name: Optional[str] = None, 
    settings: Optional[Settings] = None,
    prompt_type: PromptType = PromptType.DEFAULT,
) -> RetrievalQA:
    """Build a RetrievalQA chain without memory for stateless question answering."""
    # get the LLM instance (Gemini)
    llm = get_llm(model_name=model_name, settings=settings)
    # get the prompt template based on prompt type
    prompt = get_prompt(prompt_type=prompt_type)
    
    # create a RetrievalQA chain that combines retriever + LLM
    # chain_type="stuff" means all retrieved documents are concatenated into the prompt
    # return_source_documents=True includes source docs in the response
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )


def build_conversational_chain(
    retriever,
    model_name: Optional[str] = None,
    memory=None,
    verbose: bool = True,
    settings: Optional[Settings] = None,
    prompt_type: PromptType = PromptType.DEFAULT,
) -> ConversationalRetrievalChain:
    """
    Build a ConversationalRetrievalChain with memory for multi-turn conversations.
    
    If memory is not provided, uses the cached global memory to maintain
    conversation continuity across requests.
    """
    # get the LLM instance (Gemini)
    llm = get_llm(model_name=model_name, settings=settings)
    # get the prompt template based on prompt type
    prompt = get_prompt(prompt_type=prompt_type)
    # use provided memory or get cached global memory for conversation continuity
    # this ensures all requests share the same conversation history
    memory = memory or get_memory()
    
    # create a ConversationalRetrievalChain that combines retriever + LLM + memory
    # this chain can handle follow-up questions by maintaining conversation context
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        verbose=verbose,
    )

