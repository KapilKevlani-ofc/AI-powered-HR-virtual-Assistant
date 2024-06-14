import asyncio
import streamlit as st
from src.components.database_management import Database_Manager
from src.pipelines.language_model_processor import LanguageModelProcessor
from src.pipelines.speechtotext import get_transcript
from src.pipelines.texttospeech import TextToSpeech 
from src.components.data_ingestion import load_pdf
from src.components.data_transformation import split_text
import asyncio
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone
import os


class StreamlitConversationManager():
    def __init__(self):
        self.transcription_response = ""
        self.llm = LanguageModelProcessor()
    async def main(self):
        def handle_full_sentence(full_sentence):
            self.transcription_response = full_sentence
            st.session_state.messages.append(f"Human: {full_sentence}")
        while st.session_state.conversation_active:
            await get_transcript(handle_full_sentence)
            if "goodbye" in self.transcription_response.lower():
                st.session_state.conversation_active = False
                break
            llm_response = self.llm.process(self.transcription_response)
            tts = TextToSpeech()
            tts.speak(llm_response)
            st.session_state.messages.append(f"LLM: {llm_response}")
st.title("Voice-to-Voice Virtual Assistant")
st.sidebar.title("Controls")
start_button = st.sidebar.button("Start Conversation")
end_button = st.sidebar.button("End Conversation")
if 'conversation_active' not in st.session_state:
   st.session_state.conversation_active = False
if start_button:
   st.session_state.conversation_active = True
   st.session_state.messages = []
if end_button:
   st.session_state.conversation_active = False
if st.session_state.conversation_active:
   st.write("Listening...")
if 'manager' not in st.session_state:
   st.session_state.manager = StreamlitConversationManager()
async def run_conversation():
   await st.session_state.manager.main()
if st.session_state.conversation_active:
   asyncio.run(run_conversation())
if 'messages' in st.session_state:
   for msg in st.session_state.messages:
       st.write(msg)
