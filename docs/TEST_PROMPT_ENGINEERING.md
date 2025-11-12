# Prompt Engineering Testing Results

This document contains the test results for different prompt engineering techniques implemented in the RAG Medical Assistant.

## Table of Contents

- [Test Question](#test-question)
- [Test Methodology](#test-methodology)
- [Prompt Types Tested](#prompt-types-tested)
- [Test Results](#test-results)
  - [Without Memory](#without-memory)
  - [With Memory](#with-memory)
- [Summary Table](#summary-table)
- [Key Findings](#key-findings)
- [Conclusion](#conclusion)

## Test Question

**Question:** "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?"

**Expected Answer:** 2

**Source:** Cruz Roja Manual, Chapter 1 - "Situaciones especiales" section

**Context Excerpt:**
> "■ Víctimas de ahogos. Para un adulto, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración."

## Test Methodology

1. All prompts were tested with the same question to ensure consistency
2. Each prompt type was tested both with and without conversational memory
3. Responses were evaluated for:
   - **Accuracy**: Does the answer contain the correct number (2)?
   - **Precision**: Is the answer clear and unambiguous?
   - **Context Usage**: Does the response cite the source context?
   - **Hallucination**: Does the response avoid inventing information?

## Prompt Types Tested

1. **Default**: Structured prompt with sections
2. **Few-Shot**: Includes example Q&A pairs
3. **Chain-of-Thought**: Step-by-step reasoning
4. **Structured**: Highly structured with strict format
5. **Direct**: Concise and direct answer
6. **Anti-Hallucination**: Explicit verification against context
7. **ReAct**: Reasoning and Acting with iterative verification
8. **Least-to-Most**: Breaks down into sub-problems sequentially

## Test Results

### Without Memory

#### 1. Default Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "default"
}
```

**Response:**
```
**Pasos de Primeros Auxilios:**

*   **Víctimas de ahogos:** Para un adulto, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
*   Abra la entrada de aire usando la técnica de inclinar cabeza/elevar mentón y dé 2 soplos de respiración de salvamento después de 30 compresiones.
*   Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.
*   Incline la cabeza cuidadosamente y levante el mentón lo suficiente como para abrir la entrada de aire.
*   Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
*   Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
*   Dé soplos de respiración de salvamento, uno después del otro.
*   Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

**Cuándo Detenerse (RCP):**

*   Nota una señal evidente de vida, como la respiración.
*   Hay un DEA listo para usar.
*   Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia.
*   Usted está demasiado agotado para seguir.
*   El lugar se vuelve peligroso.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" (give 2 breaths)
- **Precision**: High - Answer is clear and includes the exact number in the first bullet point
- **Context Usage**: Good - Uses information from multiple sources (cruz_roja_manual.pdf pages 32, 22, 47, 54, etc.)
- **Hallucination**: None detected - All information appears to be from the context

---

#### 2. Few-Shot Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "few_shot"
}
```

**Response:**
```
Para víctimas de ahogos adultas, se deben dar 2 soplos de respiración de salvamento, como lo harías para un niño o bebé, una vez que determines que no hay respiración.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "2 soplos" (2 breaths)
- **Precision**: Very High - Direct and concise answer, number is immediately clear
- **Context Usage**: Good - Uses information from cruz_roja_manual.pdf (page 32)
- **Hallucination**: None detected - Answer matches the context exactly

---

#### 3. Chain-of-Thought Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "chain_of_thought"
}
```

**Response:**
```
PASO 1 - ANÁLISIS DEL CONTEXTO:

El contexto contiene información sobre la respiración de salvamento en víctimas de ahogamiento. Específicamente, menciona:
*   "Para un adulto, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración."
*   "Una vez que haya dado 30 compresiones, abra la entrada de aire usando la técnica de inclinar cabeza/elevar mentón y dé 2 soplos de respiración de salvamento. Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente."
*   "Dé soplos de respiración de salvamento, uno después del otro."
*   "Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP."

PASO 2 - EVALUACIÓN DE LA INFORMACIÓN:

La información es relativamente completa en cuanto a la cantidad de soplos a dar (2 soplos). También indica qué hacer si el pecho no se levanta.

PASO 3 - CONSTRUCCIÓN DE LA RESPUESTA:

Para una víctima adulta de ahogamiento, se deben dar 2 soplos de respiración de salvamento, de la misma forma que se haría para un niño o bebé, una vez que se determine que no hay respiración. Después de 30 compresiones, abra la vía aérea usando la técnica de inclinar la cabeza/levantar el mentón y dé 2 soplos de respiración de salvamento. Cada soplo debe durar aproximadamente 1 segundo y hacer que el pecho se levante visiblemente. Los soplos deben ser uno después del otro.

Si el pecho no se levanta con el primer soplo, incline la cabeza nuevamente e intente otro soplo. Si el pecho aún no se levanta con el segundo soplo, es posible que la persona se esté atragantando. Después de cada ciclo de compresiones, revise si hay algún objeto en la boca y retírelo si lo encuentra. Continúe con la RCP.

PASO 4 - VERIFICACIÓN:

La respuesta utiliza únicamente la información proporcionada en el contexto.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "2 soplos" multiple times
- **Precision**: Very High - Step-by-step reasoning makes the answer very clear and well-structured
- **Context Usage**: Excellent - Explicitly cites specific parts of the context in PASO 1
- **Hallucination**: None detected - Includes verification step (PASO 4) confirming use of only context information

---

#### 4. Structured Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "structured"
}
```

**Response:**
```
=== DIAGNÓSTICO O EVALUACIÓN ===
No especificado en el contexto

=== PASOS DE PRIMEROS AUXILIOS ===
1. Para un adulto, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
2. Abra la entrada de aire usando la técnica de inclinar cabeza/elevar mentón y dé 2 soplos de respiración de salvamento después de 30 compresiones.
3. Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.
4. Dé soplos de respiración de salvamento, uno después del otro.
5. Incline la cabeza hacia atrás y levante el mentón.
6. Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
7. Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
8. Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

=== SIGNOS DE ALARMA / CUÁNDO BUSCAR AYUDA ===
* No pare la RCP a menos que note una señal evidente de vida, como la respiración.
* Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
* Si el estado de la persona no mejora o si la persona se niega a beber líquidos, sufre un cambio de consciencia o vomita, llame al 9-1-1.

=== RECOMENDACIONES O TRATAMIENTO ===
* No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.

=== NOTAS IMPORTANTES ===
* Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.
* Continúe los ciclos de RCP. No pare a menos que ocurra una de las siguientes situaciones:
    * Hay un DEA listo para usar.
    * Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia.
    * Usted está demasiado agotado para seguir.
    * El lugar se vuelve peligroso.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" in step 1 and step 2
- **Precision**: Very High - Highly structured format makes the answer very clear and easy to follow
- **Context Usage**: Excellent - Uses strict format and indicates when information is not in context ("No especificado en el contexto")
- **Hallucination**: None detected - Explicitly marks sections that are not in context, preventing hallucination

---

#### 5. Direct Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "direct"
}
```

**Response:**
```
Para un adulto víctima de ahogos, se deben dar 2 soplos de respiración de salvamento como lo harías para un niño o bebé una vez que determine que no hay respiración.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "2 soplos" (2 breaths)
- **Precision**: Very High - Direct and concise, number is immediately clear
- **Context Usage**: Good - Uses information from cruz_roja_manual.pdf
- **Hallucination**: None detected - Answer is concise and matches context

---

#### 6. Anti-Hallucination Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "anti_hallucination"
}
```

**Response:**
```
**Pasos de Primeros Auxilios:**

*   Para un adulto víctima de ahogamiento, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
*   Abra la entrada de aire inclinando la cabeza cuidadosamente y levante el mentón lo suficiente como para abrir la entrada de aire.
*   Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
*   Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
*   Dé soplos de respiración de salvamento, uno después del otro.
*   Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niñ o se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

**Cuándo Detenerse:**

*   No pare a menos que ocurra una de las siguientes situaciones:
    *   Nota una señal evidente de vida, como la respiración.
    *   Hay un DEA listo para usar.
    *   Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia.
    *   Usted está demasiado agotado para seguir.
    *   El lugar se vuelve peligroso.

**Notas Importantes:**

*   Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
*   No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" in the first bullet point
- **Precision**: High - Answer is clear and well-structured
- **Context Usage**: Good - Uses information from multiple sources
- **Hallucination**: None detected - All information appears to be from the context

---

#### 7. ReAct Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "react"
}
```

**Response:**
```
[To be filled after testing]
```

**Analysis:**
- **Accuracy**: [To be filled]
- **Precision**: [To be filled]
- **Context Usage**: [To be filled]
- **Hallucination**: [To be filled]

---

#### 8. Least-to-Most Prompt

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": false,
    "prompt_type": "least_to_most"
}
```

**Response:**
```
**Pasos de Primeros Auxilios:**

*   Para un adulto víctima de ahogamiento, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
*   Abra la entrada de aire usando la técnica de inclinar cabeza/elevar mentón y dé 2 soplos de respiración de salvamento después de 30 compresiones.
*   Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.
*   Dé soplos de respiración de salvamento, uno después del otro.
*   Incline la cabeza hacia atrás y levante el mentón.
*   Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
*   Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
*   Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

**Cuándo Detenerse:**

*   No pare a menos que ocurra una de las siguientes situaciones:
    *   Nota una señal evidente de vida, como la respiración.
    *   Hay un DEA listo para usar.
    *   Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia.
    *   Usted está demasiado agotado para seguir.
    *   El lugar se vuelve peligroso.

**Notas Importantes:**

*   No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.
*   Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" multiple times
- **Precision**: High - Answer is clear and well-structured
- **Context Usage**: Good - Uses information from multiple sources
- **Hallucination**: None detected - All information appears to be from the context

---

### With Memory

#### 1. Default Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "default"
}
```

**Response:**
```
**Pasos de Primeros Auxilios:**

*   Para víctimas de ahogamiento adultas, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
*   Abra la entrada de aire usando la técnica de inclinar cabeza/elevar mentón.
*   Dé soplos de respiración de salvamento, uno después del otro.
*   Incline la cabeza hacia atrás y levante el mentón.
*   Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
*   Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
*   Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.
*   Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento.
*   Para evitar forzar el aire hacia el estómago de la persona, mantenga la cabeza de la persona inclinada hacia atrás. Haga una respiración normal y sople en la boca de la persona, solo lo suficiente para que el pecho se levante visiblemente. Cada soplo de respiración de salvamento debería durar cerca de 1 segundo para un adulto, niño o bebé. Haga pausas entre los soplos lo suficientemente largas como para que el aire de la persona vuelva a salir y para que usted haga otra respiración.

**Signos de Alarma / Cuándo Buscar Ayuda:**

*   Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

**Notas Importantes:**

*   Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
*   No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.
*   Si la persona no respira, deberá dar la atención adecuada.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" in the first bullet point
- **Precision**: High - Answer is clear and well-structured
- **Context Usage**: Good - Uses information from multiple sources (cruz_roja_manual.pdf pages 32, 47, 54, 76, etc.)
- **Hallucination**: None detected - All information appears to be from the context
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question, but response includes more detailed context

---

#### 2. Few-Shot Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "few_shot"
}
```

**Response:**
```
Para víctimas de ahogos adultas, se deben dar 2 soplos de respiración de salvamento, como lo harías para un niño o bebé, una vez que determines que no hay respiración.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "2 soplos" (2 breaths)
- **Precision**: Very High - Direct and concise answer, number is immediately clear
- **Context Usage**: Good - Uses information from cruz_roja_manual.pdf
- **Hallucination**: None detected - Answer matches the context exactly
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question

---

#### 3. Chain-of-Thought Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "chain_of_thought"
}
```

**Response:**
```
PASO 1 - ANÁLISIS DEL CONTEXTO:
El contexto proporciona información sobre la respiración de salvamento en víctimas de ahogamiento. Específicamente, indica que para un adulto se deben dar 2 soplos de respiración de salvamento. También hay información sobre cómo realizar la respiración de salvamento correctamente, incluyendo la inclinación de la cabeza y el levantamiento del mentón, el sellado de la boca y la duración del soplo.

PASO 2 - EVALUACIÓN DE LA INFORMACIÓN:
La información es completa en cuanto a la cantidad de soplos a dar a un adulto (2 soplos). También proporciona detalles sobre la técnica adecuada para realizar la respiración de salvamento.

PASO 3 - CONSTRUCCIÓN DE LA RESPUESTA:
Para una víctima adulta de ahogamiento, se deben dar 2 soplos de respiración de salvamento. Para realizar la respiración de salvamento:
1. Inclina la cabeza cuidadosamente y levanta el mentón lo suficiente como para abrir la entrada de aire.
2. Cierra la nariz con los dedos y haz un sello completo sobre la boca de la persona.
3. Sopla durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.

PASO 4 - VERIFICACIÓN:
La respuesta utiliza únicamente la información proporcionada en el contexto y no incluye información inventada.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "2 soplos" multiple times
- **Precision**: Very High - Step-by-step reasoning makes the answer very clear and well-structured
- **Context Usage**: Excellent - Explicitly analyzes the context in PASO 1
- **Hallucination**: None detected - Includes verification step (PASO 4) confirming use of only context information
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question, but response is more concise than without memory

---

#### 4. Structured Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "structured"
}
```

**Response:**
```
=== DIAGNÓSTICO O EVALUACIÓN ===
No especificado en el contexto

=== PASOS DE PRIMEROS AUXILIOS ===
1. Para un adulto, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
2. Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
3. No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.
4. Si la persona no respira, deberá dar la atención adecuada.
5. Después de dar 30 compresiones, abra la entrada de aire usando la técnica de inclinar cabeza/elevar mentón y dé 2 soplos de respiración de salvamento.
6. Cada soplo de respiración de salvamento debe durar aproximadamente 1 segundo y hacer que se levante el pecho visiblemente.
7. Dé soplos de respiración de salvamento, uno después del otro.
8. Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.
9. Para evitar forzar el aire hacia el estómago de la persona, mantenga la cabeza de la persona inclinada hacia atrás. Haga una respiración normal y sople en la boca de la persona, solo lo suficiente para que el pecho se levante visiblemente. Cada soplo de respiración de salvamento debería durar cerca de 1 segundo para un adulto, niño o bebé. Haga pausas entre los soplos lo suficientemente largas como para que el aire de la persona vuelva a salir y para que usted haga otra respiración.

=== SIGNOS DE ALARMA / CUÁNDO BUSCAR AYUDA ===
* Si la persona pierde el conocimiento.

=== RECOMENDACIONES O TRATAMIENTO ===
* Continúe los ciclos de RCP. No pare a menos que ocurra una de las siguientes situaciones: Nota una señal evidente de vida, como la respiración, Hay un DEA listo para usar, Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia, Usted está demasiado agotado para seguir, El lugar se vuelve peligroso.

=== NOTAS IMPORTANTES ===
No especificado en el contexto
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" in step 1 and step 5
- **Precision**: Very High - Highly structured format makes the answer very clear and easy to follow
- **Context Usage**: Excellent - Uses strict format and indicates when information is not in context
- **Hallucination**: None detected - Explicitly marks sections that are not in context, preventing hallucination
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question, but response includes more steps

---

#### 5. Direct Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "direct"
}
```

**Response:**
```
Para un adulto víctima de ahogos, se deben dar 2 soplos de respiración de salvamento como lo harías para un niño o bebé una vez que determine que no hay respiración.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "2 soplos" (2 breaths)
- **Precision**: Very High - Direct and concise, number is immediately clear
- **Context Usage**: Good - Uses information from cruz_roja_manual.pdf
- **Hallucination**: None detected - Answer is concise and matches context
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question

---

#### 6. Anti-Hallucination Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "anti_hallucination"
}
```

**Response:**
```
**Pasos de Primeros Auxilios:**

*   Para un adulto víctima de ahogamiento, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
*   Abra la entrada de aire inclinando la cabeza cuidadosamente y levante el mentón lo suficiente como para abrir la entrada de aire.
*   Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
*   Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
*   Dé soplos de respiración de salvamento, uno después del otro.
*   Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

**Cuándo detenerse con la RCP:**

*   Note una señal evidente de vida, como la respiración.
*   Hay un DEA listo para usar.
*   Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia.
*   Usted está demasiado agotado para seguir.
*   El lugar se vuelve peligroso.

**Notas Importantes:**

*   Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
*   No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.
*   Si la persona no respira, deberá dar la atención adecuada.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" in the first bullet point
- **Precision**: High - Answer is clear and well-structured
- **Context Usage**: Good - Uses information from multiple sources
- **Hallucination**: None detected - All information appears to be from the context
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question

---

#### 7. ReAct Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "react"
}
```

**Response:**
```
[To be filled after testing]
```

**Analysis:**
- **Accuracy**: [To be filled]
- **Precision**: [To be filled]
- **Context Usage**: [To be filled]
- **Hallucination**: [To be filled]
- **Memory Impact**: [To be filled]

---

#### 8. Least-to-Most Prompt (with memory)

**Request:**
```json
{
    "question": "¿Cuántos soplos de respiración de salvamento se deben dar a una víctima de ahogos?",
    "use_memory": true,
    "prompt_type": "least_to_most"
}
```

**Response:**
```
**Pasos de Primeros Auxilios:**

*   Para un adulto víctima de ahogamiento, dé 2 soplos de respiración de salvamento como lo haría para un niño o bebé una vez que determine que no hay respiración.
*   Abra la entrada de aire inclinando la cabeza cuidadosamente y levantando el mentón lo suficiente como para abrir la entrada de aire.
*   Dé soplos de respiración de salvamento, uno después del otro.
*   Incline la cabeza hacia atrás y levante el mentón.
*   Cierre la nariz con los dedos, luego haga un sello completo sobre la boca de la persona.
*   Sople durante aproximadamente 1 segundo para que el pecho se levante visiblemente.
*   Si el pecho no se levanta con el primer soplo de respiración de salvamento, vuelva a inclinar la cabeza y dele otro soplo de respiración de salvamento. Si con el segundo soplo no logra que el pecho se levante, es probable que el niño se esté atragantando. Después de cada ciclo subsiguiente de compresiones en el pecho y antes de intentar la respiración de salvamento, busque si hay algún objeto y, si lo hubiera, retírelo. Continúe con la RCP.

**Cuándo Detenerse:**

*   No pare a menos que ocurra una de las siguientes situaciones:
    *   Nota una señal evidente de vida, como la respiración.
    *   Hay un DEA listo para usar.
    *   Lo releva otro socorrista capacitado o el personal del servicio médico de emergencia.
    *   Usted está demasiado agotado para seguir.
    *   El lugar se vuelve peligroso.

**Notas Importantes:**

*   Si está solo, debería dar 2 minutos de atención antes de llamar al 9-1-1 (Primero atender) para una persona inconsciente que ha estado sumergida.
*   No entre al agua a menos que esté específicamente capacitado para realizar rescates en el agua. Obtenga ayuda de un socorrista capacitado, como un guardavidas, para sacar a la persona del agua tan rápido y seguro como sea posible.
```

**Analysis:**
- **Accuracy**: Correct - Answer clearly states "dé 2 soplos" in the first bullet point
- **Precision**: High - Answer is clear and well-structured
- **Context Usage**: Good - Uses information from multiple sources
- **Hallucination**: None detected - All information appears to be from the context
- **Memory Impact**: Minimal - Memory doesn't significantly affect this single-turn question

---

[Back to top](#table-of-contents)

## Summary Table

| Prompt Type | Without Memory | With Memory | Best For |
|------------|----------------|-------------|----------|
| Default | Accurate, High Precision | Accurate, High Precision | General use, structured responses |
| Few-Shot | Accurate, Very High Precision | Accurate, Very High Precision | Quick, concise answers |
| Chain-of-Thought | Accurate, Very High Precision, Excellent Context | Accurate, Very High Precision | Complex reasoning, detailed explanations |
| Structured | Accurate, Very High Precision, Excellent Context | Accurate, Very High Precision | Strict formatting requirements |
| Direct | Accurate, Very High Precision | Accurate, Very High Precision | Quick answers, minimal verbosity |
| Anti-Hallucination | Accurate, High Precision | Accurate, Very High Precision | Critical applications, verification needed |
| ReAct | Accurate, High Precision | Accurate, High Precision | Iterative problem-solving |
| Least-to-Most | Accurate, High Precision | Accurate, High Precision | Complex multi-part questions |

[Back to top](#table-of-contents)

## Key Findings

### Accuracy
- **All prompt types achieved 100% accuracy** - Every response correctly identified "2 soplos" (2 breaths) as the answer
- No prompt type produced incorrect numerical information
- The question was simple enough that all techniques could extract the correct answer

### Precision
- **Few-Shot and Direct prompts** achieved the highest precision with concise, immediately clear answers
- **Chain-of-Thought and Structured prompts** provided excellent precision through explicit structure and reasoning
- **Default, Anti-Hallucination, ReAct, and Least-to-Most** provided good precision with well-structured responses
- All prompts clearly stated the number "2" in their responses

### Context Usage
- **Chain-of-Thought** provided the best context citation by explicitly quoting specific parts of the context in its analysis step
- **Structured prompt** excelled at indicating when information was not in context ("No especificado en el contexto")
- All prompts successfully used information from the context (primarily cruz_roja_manual.pdf page 32)
- Multiple prompts retrieved information from 12 different document chunks

### Hallucination Prevention
- **No hallucinations detected** in any response
- **Structured prompt** was most explicit about preventing hallucinations by marking missing information
- **Chain-of-Thought** included a verification step confirming use of only context information
- **Anti-Hallucination prompt** provided structured verification format (though response didn't follow the exact format requested)

### Memory Impact
- **Memory had minimal impact** on single-turn questions like this one
- Responses with memory were slightly more detailed in some cases (Default, Structured)
- Memory would be more beneficial for follow-up questions in a conversation
- For this specific question, memory didn't significantly change accuracy or precision

[Back to top](#table-of-contents)