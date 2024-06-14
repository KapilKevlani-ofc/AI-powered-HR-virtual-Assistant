import asyncio
import streamlit as st
from src.components.database_management import Database_Manager
from src.pipelines.language_model_processor import LanguageModelProcessor
from src.pipelines.texttospeech import TextToSpeech 
from src.components.data_ingestion import load_pdf
from src.components.data_transformation import split_text
import asyncio
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone
from src.pipelines.transcript_collector import TranscriptCollector
import os


async def get_transcript(callback):
   transcription_complete = asyncio.Event()  # Event to signal transcription completion
   try:
       config = DeepgramClientOptions(options={"keepalive": "true"})
       deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"), config)
       dg_connection = deepgram.listen.asynclive.v("1")
       print("Listening...")
       async def on_message(self, result, **kwargs):
           sentence = result.channel.alternatives[0].transcript
           if not result.speech_final:
               TranscriptCollector.add_part(sentence)
           else:
               # This is the final part of the current sentence
               TranscriptCollector.add_part(sentence)
               full_sentence = TranscriptCollector.get_full_transcript()
               # Check if the full_sentence is not empty before printing
               if len(full_sentence.strip()) > 0:
                   full_sentence = full_sentence.strip()
                   print(f"Human: {full_sentence}")
                   callback(full_sentence)  # Call the callback with the full_sentence
                   TranscriptCollector.reset()
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