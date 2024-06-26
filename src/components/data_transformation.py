from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(extracted_data):
   text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
   text_chunks = text_splitter.split_documents(extracted_data)
   return text_chunks
