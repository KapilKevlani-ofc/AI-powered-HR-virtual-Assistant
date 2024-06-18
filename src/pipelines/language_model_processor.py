import os
import time
from src.components.database_management import Database_Manager
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from src.components.data_ingestion import store_timings_to_csv
from langchain.prompts import (
   ChatPromptTemplate,
   MessagesPlaceholder,
   SystemMessagePromptTemplate,
   HumanMessagePromptTemplate,
)
dbm = Database_Manager()
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
       raw_prompt = PromptTemplate.from_template(
           """
<s>[INST] You are a technical assistant good at searching documents. If you do not have an answer from the provided information just do not make up answers and clearly say that I do not know. [/INST] </s>
               [INST] {input}
                   Context: {context}
                   Answer:
               [/INST]
           """
       )
       vector_store = dbm.manage_database()
       retriever = dbm.retriever_object(vector_store)
       self.document_chain = create_stuff_documents_chain(self.llm, raw_prompt)
       self.chain = create_retrieval_chain(retriever, self.document_chain)
   def process(self, text):
       self.memory.chat_memory.add_user_message(text)
       start_time = time.time()
       response = self.chain.invoke({"input": text})
       response_text = response['answer']
       end_time = time.time()
       self.memory.chat_memory.add_ai_message(response_text)
       elapsed_time = int((end_time - start_time) * 1000)
       print(f"LLM ({elapsed_time}ms): {response_text}")
       store_timings_to_csv('LLM_Response', elapsed_time)
       return response_text
