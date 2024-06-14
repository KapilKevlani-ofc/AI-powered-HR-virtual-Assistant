import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import FastEmbedEmbeddings
from langchain.vectorstores import Chroma
import chromadb
class Database_Manager():
   @staticmethod
   def load_pdf():
       loader = DirectoryLoader('./data', glob="./*.pdf", loader_cls=PyMuPDFLoader)
       documents = loader.load()
       return documents
   @staticmethod
   def text_split(extracted_data):
       text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
       text_chunks = text_splitter.split_documents(extracted_data)
       return text_chunks
   @staticmethod
   def manage_database():
       folder_path = "DB"
       # Check if the folder exists and has data
       if os.path.exists(folder_path) and os.listdir(folder_path):
           client = chromadb.Client()

            # Connect to the vector store.
           client.connect()

            # Get the vector store.
           vector_store = client.get_vector_store("vector_store")
           print("Folder exists and has data. Doing nothing.")
           vector_store = Chroma.from_documents(
               documents=text_chunks, embedding=embeddings, persist_directory=folder_path)
       else:
           print("Folder does not exist or is empty. Creating folder and storing data.")
           extracted_data = Database_Manager.load_pdf()
           text_chunks = Database_Manager.text_split(extracted_data)
           embeddings = FastEmbedEmbeddings()
           vector_store = Chroma.from_documents(
               documents=text_chunks, embedding=embeddings, persist_directory=folder_path)
           vector_store.persist()
# # Run the database management process
# Database_Manager.manage_database()