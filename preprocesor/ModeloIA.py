from llama_cpp import Llama

llm = Llama(
    model_path="preprocesor/openhermes-2.5-mistral-7b.Q2_K.gguf",
    n_ctx=8192,
    n_threads=6,
    verbose=False
)

def pedir_consulta(consul,chunks):
      prompt=f'''En base a los archivos que tenes a disposicion dados

      Pregunta: {consul}
      Respuesta: '''
      output = llm(
            prompt,
            max_tokens=10,
            echo=True
    )

      return output['choices'][0].get("text", "")

# Prueba