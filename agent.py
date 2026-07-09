import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class BimBamAgent:
    def __init__(self, vector_store_path: str = "faiss_index"):
        if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
            raise ValueError("No se encontró GOOGLE_API_KEY en las variables de entorno. Configúrala en el archivo .env")
            
        print("Cargando base de datos vectorial de políticas...")
        # Cargar embeddings y vector store
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # Permitir la deserialización peligrosa porque nosotros mismos creamos el archivo faiss localmente
        self.vectorstore = FAISS.load_local(
            vector_store_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Crear el retriever (recuperador de información)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Inicializar el LLM (Google Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        
        # Crear el prompt del sistema
        system_prompt = (
            "Eres el asistente virtual oficial de BimBam Buy, un E-commerce. "
            "Tu objetivo es ayudar a los clientes respondiendo sus preguntas basándote ÚNICAMENTE en la siguiente información de contexto proporcionada de nuestras políticas.\n\n"
            "Si no sabes la respuesta o no está en el contexto, simplemente di 'Lo siento, no tengo esa información en las políticas actuales de BimBam Buy. Por favor, contacta a soporte.' "
            "No inventes información bajo ninguna circunstancia. Responde de forma amable, clara y concisa en español.\n\n"
            "Contexto:\n{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        # Crear la cadena de Retrieval-Augmented Generation (RAG)
        self.question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, self.question_answer_chain)
        
    def ask(self, question: str) -> str:
        response = self.rag_chain.invoke({"input": question})
        return response["answer"]

if __name__ == "__main__":
    # Prueba rápida en terminal
    try:
        agent = BimBamAgent()
        pregunta = "¿Cuánto tiempo tengo para devolver un producto?"
        print(f"\nPregunta: {pregunta}")
        print(f"Respuesta: {agent.ask(pregunta)}")
    except Exception as e:
        print(f"Error: {e}")
