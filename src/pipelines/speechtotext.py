import asyncio
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone
import os


class TranscriptCollector:
   transcript_parts = []
   @staticmethod
   def reset():
       TranscriptCollector.transcript_parts = []
   @staticmethod
   def add_part(part):
       TranscriptCollector.transcript_parts.append(part)
   @staticmethod
   def get_full_transcript():
       return ' '.join(TranscriptCollector.transcript_parts)
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
       

