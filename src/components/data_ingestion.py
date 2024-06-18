from langchain_community.document_loaders import PyMuPDFLoader
from langchain.document_loaders import DirectoryLoader
import csv
def load_pdf():
   loader = DirectoryLoader('./data', glob="./*.pdf", loader_cls=PyMuPDFLoader)
   documents = loader.load()
   return documents

def store_timings_to_csv(process_name, elapsed_time):
       csv_file_path = "./latency_track.csv"
       with open(csv_file_path, mode='a', newline='') as file:
           writer = csv.writer(file)
           writer.writerow([process_name, elapsed_time])
