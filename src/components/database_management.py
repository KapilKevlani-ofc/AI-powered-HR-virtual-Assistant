import os
from src.components.data_ingestion import load_pdf
from src.components.data_transformation import split_text
from langchain.embeddings import FastEmbedEmbeddings
from langchain.vectorstores import Chroma
class Database_Manager:
   @staticmethod
   def manage_database():
       folder_path = "DB"
       embeddings = FastEmbedEmbeddings()
       # Check if the vector store already exists and load it if it does
       if os.path.exists(folder_path) and os.listdir(folder_path):
           print("Loading existing Vector_store")
           vector_store = Chroma(embedding_function=embeddings, persist_directory=folder_path)
       else:
           # Otherwise, create a new vector store
           print("Folder does not exist or is empty. Creating folder and storing data.")
           extracted_data = load_pdf()
           text_chunks = split_text(extracted_data)
           vector_store = Chroma.from_documents(
               documents=text_chunks, embedding=embeddings, persist_directory=folder_path
           )
       return vector_store
   @staticmethod
   def retriever_object(vector_store):
       retriever = vector_store.as_retriever(
           search_type="similarity_score_threshold",
           search_kwargs={
               "k": 20,
               "score_threshold": 0.1,
           }
       )
       return retriever
