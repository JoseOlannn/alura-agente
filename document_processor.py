import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def process_documents(directory_path: str, vector_store_path: str = "faiss_index"):
    print(f"Cargando documentos PDF desde el directorio: {directory_path}")
    
    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()
    print(f"Se cargaron {len(documents)} páginas en total de los PDFs.")

    # Cargar también el archivo CSV de políticas antiguas
    csv_path = os.path.join(directory_path, "bimbam_buy_politicas.csv")
    if os.path.exists(csv_path):
        from langchain_community.document_loaders.csv_loader import CSVLoader
        csv_loader = CSVLoader(file_path=csv_path)
        csv_docs = csv_loader.load()
        documents.extend(csv_docs)
        print(f"Se cargaron {len(csv_docs)} filas adicionales del CSV.")
    
    # Dividir el texto en chunks más pequeños 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    print(f"Creando embeddings y guardando en FAISS...")
    
    # Inicializar embeddings de Google (requiere GOOGLE_API_KEY en .env)
    if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
        print("\n[!] ADVERTENCIA: No se encontró una GOOGLE_API_KEY válida en las variables de entorno.")
        print("[!] Por favor, obtén tu API Key gratuita en https://aistudio.google.com/ y colócala en el archivo .env\n")
        return
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # Crear el vector store
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # Guardar localmente
    vectorstore.save_local(vector_store_path)
    print(f"¡Éxito! Base de datos vectorial guardada en el directorio: {vector_store_path}")

if __name__ == "__main__":
    # Ruta relativa a la carpeta de datos
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    process_documents(data_dir)
