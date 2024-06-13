import asyncio
import shutil
import subprocess
import requests
import time
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
   ChatPromptTemplate,
   MessagesPlaceholder,
   SystemMessagePromptTemplate,
   HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import FastEmbedEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader
from deepgram import (
   DeepgramClient,
   DeepgramClientOptions,
   LiveTranscriptionEvents,
   LiveOptions,
   Microphone,
)

def load_pdf():
   loader = DirectoryLoader('D:/AI powered HR Voice Assistant/Data Prepration', glob="./*.pdf", loader_cls=PyMuPDFLoader)
   documents = loader.load()
   return documents
extracted_data = load_pdf()
def text_split(extracted_data):
   text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
   text_chunks = text_splitter.split_documents(extracted_data)
   return text_chunks
text_chunks = text_split(extracted_data)
embeddings = FastEmbedEmbeddings()
folder_path = "DB"
vector_store = Chroma.from_documents(
   documents=text_chunks, embedding=embeddings, persist_directory=folder_path)
raw_prompt = PromptTemplate.from_template(
   """
<s>[INST] You are a technical assistant good at searching documents. If you do not have an answer from the provided information just do not make up answers and clearly say that I do not know. [/INST] </s>
   [INST] {input}
          Context: {context}
          Answer:
   [/INST]
"""
)
retriever = vector_store.as_retriever(search_type="similarity_score_threshold",
                                     search_kwargs={
                                         "k": 20,
                                         "score_threshold": 0.1,
                                     })
class LanguageModelProcessor:
   def __init__(self):
       self.llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768", groq_api_key=os.getenv("GROQ_API_KEY"))
       self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
       self.prompt = ChatPromptTemplate.from_messages([
           SystemMessagePromptTemplate.from_template(""),
           MessagesPlaceholder(variable_name="chat_history"),
           HumanMessagePromptTemplate.from_template("{text}")
       ])
       self.conversation = LLMChain(
           llm=self.llm,
           prompt=self.prompt,
           memory=self.memory
       )
       self.document_chain = create_stuff_documents_chain(self.llm, raw_prompt)
       self.chain = create_retrieval_chain(retriever, self.document_chain)
   def process(self, text):
       self.memory.chat_memory.add_user_message(text)  # Add user message to memory
       start_time = time.time()
       # Go get the response from the RAG model
       response = self.chain.invoke({"input": text})
       response_text = response['answer']
       end_time = time.time()
       self.memory.chat_memory.add_ai_message(response_text)  # Add AI response to memory
       elapsed_time = int((end_time - start_time) * 1000)
       print(f"LLM ({elapsed_time}ms): {response_text}")
       return response_text

class TextToSpeech:
   DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
   MODEL_NAME = "aura-helios-en"  # Example model name, change as needed
   @staticmethod
   def is_installed(lib_name: str) -> bool:
       lib = shutil.which(lib_name)
       return lib is not None
   def speak(self, text):
       if not self.is_installed("ffplay"):
           raise ValueError("ffplay not found, necessary to stream audio.")
       DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={self.MODEL_NAME}&performance=some&encoding=linear16&sample_rate=24000"
       headers = {
           "Authorization": f"Token {self.DG_API_KEY}",
           "Content-Type": "application/json"
       }
       payload = {
           "text": text
       }
       player_command = ["ffplay", "-autoexit", "-", "-nodisp"]
       player_process = subprocess.Popen(
           player_command,
           stdin=subprocess.PIPE,
           stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL,
       )
       start_time = time.time()  # Record the time before sending the request
       first_byte_time = None  # Initialize a variable to store the time when the first byte is received
       with requests.post(DEEPGRAM_URL, stream=True, headers=headers, json=payload) as r:
           for chunk in r.iter_content(chunk_size=1024):
               if chunk:
                   if first_byte_time is None:  # Check if this is the first chunk received
                       first_byte_time = time.time()  # Record the time when the first byte is received
                       ttfb = int((first_byte_time - start_time) * 1000)  # Calculate the time to first byte
                       print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")
                   player_process.stdin.write(chunk)
                   player_process.stdin.flush()
       if player_process.stdin:
           player_process.stdin.close()
       player_process.wait()

class TranscriptCollector:
   def __init__(self):
       self.reset()
   def reset(self):
       self.transcript_parts = []
   def add_part(self, part):
       self.transcript_parts.append(part)
   def get_full_transcript(self):
       return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()
async def get_transcript(callback):
   transcription_complete = asyncio.Event()  # Event to signal transcription completion
   try:
       config = DeepgramClientOptions(options={"keepalive": "true"})
       deepgram: DeepgramClient = DeepgramClient("", config)
       dg_connection = deepgram.listen.asynclive.v("1")
       print("Listening...")
       async def on_message(self, result, **kwargs):
           sentence = result.channel.alternatives[0].transcript
           if not result.speech_final:
               transcript_collector.add_part(sentence)
           else:
               # This is the final part of the current sentence
               transcript_collector.add_part(sentence)
               full_sentence = transcript_collector.get_full_transcript()
               # Check if the full_sentence is not empty before printing
               if len(full_sentence.strip()) > 0:
                   full_sentence = full_sentence.strip()
                   print(f"Human: {full_sentence}")
                   callback(full_sentence)  # Call the callback with the full_sentence
                   transcript_collector.reset()
                   transcription_complete.set()  # Signal to stop transcription and exit
       dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
       options = LiveOptions(
           model="nova-2",
           punctuate=True,
           language="en-US",
           encoding="linear16",
           channels=1,
           sample_rate=16000,
           endpointing=300,
           smart_format=True,
       )
       await dg_connection.start(options)
       # Open a microphone stream on the default input device
       microphone = Microphone(dg_connection.send)
       microphone.start()
       await transcription_complete.wait()  # Wait for the transcription to complete instead of looping indefinitely
       # Wait for the microphone to close
       microphone.finish()
       # Indicate that we've finished
       await dg_connection.finish()
   except Exception as e:
       print(f"Could not open socket: {e}")
       return

class ConversationManager:
   def __init__(self):
       self.transcription_response = ""
       self.llm = LanguageModelProcessor()
   async def main(self):
       def handle_full_sentence(full_sentence):
           self.transcription_response = full_sentence
       # Loop indefinitely until "goodbye" is detected
       while True:
           await get_transcript(handle_full_sentence)
           # Check for "goodbye" to exit the loop
           if "goodbye" in self.transcription_response.lower():
               break
           llm_response = self.llm.process(self.transcription_response)
           tts = TextToSpeech()
           tts.speak(llm_response)
           # Reset transcription_response for the next loop iteration
           self.transcription_response = ""

if __name__ == "__main__":
   manager = ConversationManager()
   asyncio.run(manager.main())