from llama_cpp import Llama

llm = Llama( #creando una variable con la ia
    model_path="./models/openhermes-2.5-mistral-7b.Q4_K_M.gguf", #modelo de la IA
    n_ctx=10000, #Cantidad de transacciones/ las veces que busca
    n_threads=6, # Cantidad de hilos que usa de mi procesador
    verbose=False,
)

def pedir_consulta(consul,chunks):
      #el promp seria lo que va a despostrar
      prompt = f"""
      You are an assistant that only responds with the information found in the provided context.

      ⚠️ Important instructions:
      Always answer in spanish.
      Do not translate information.
      Do not make up information.
      Do not add details that are not in the context.
      Do not make assumptions.
      Make sure to always answer with the same format as previous answers.
      Make sure that the answer is correct.
      Make sure the answer is a single paragraph, not a list or bullet points.
      Make sure to answer in a concise manner.
      Always keep the names and emails exactly as they appear in the context.
      Stop the answer if you reach any of the following symbols: "?".
      Make sure not to add: "Question:", "Answer:", "Context:", "CONTEXT END", "CONTEXTO INICIO", "Siguiente pregunta:", "Next question:", "Pregunta siguiente:", "Next question:" or similar phrases in your answer."
      If the chunk has the simbol ":", make sure to check if the information next to it is correct and add it.
      In case of dates, make sure to add them all.
      You must provide a single, clear, and concise answer strictly based on the context.
      If you are answering the question, do not add information or details that are not in the context.
      If the context is really empty, reply exactly: "No information found in the context".

      ---CONTEXT START
      Context: {chunks}
      CONTEXT END
      ---

      Question: {consul}
      Answer:
      """
      output = llm(
            prompt,
            max_tokens=500,
            echo=False,
            stop=["\nPregunta:", "\n---", "\nSiguiente pregunta:", "\n\n"]

    )

      return output['choices'][0]['text'].strip()


# Prueba