from langchain_community.document_loaders import PyMuPDFLoader
from langchain.document_loaders import DirectoryLoader
def load_pdf():
   loader = DirectoryLoader('./data', glob="./*.pdf", loader_cls=PyMuPDFLoader)
   documents = loader.load()
   return documents