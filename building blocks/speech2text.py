import asyncio
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()

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

async def get_transcript():
    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient("", config)

        dg_connection = deepgram.listen.asynclive.v("1")

        async def on_message(self, result, **kwargs):
            # print (result)
            sentence = result.channel.alternatives[0].transcript

            print (result)
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                # This is the final part of the current sentence
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                print(f"speaker: {full_sentence}")
                # Reset the collector for the next sentence
                transcript_collector.reset()

        async def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=True
        )

        await dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()

        while True:
            if not microphone.is_active():
                break
            await asyncio.sleep(1)

        # Wait for the microphone to close
        microphone.finish()

        # Indicate that we've finished
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

if __name__ == "__main__":
    asyncio.run(get_transcript())





# # main.py (python example)

# import os
# from dotenv import load_dotenv

# from deepgram import (
#     DeepgramClient,
#     PrerecordedOptions,
#     FileSource,
# )

# load_dotenv()


# API_KEY = os.getenv("DEEPGRAM_API_KEY")


# def speech2text(audio_file):
#     try:
#         # STEP 1 Create a Deepgram client using the API key
#         deepgram = DeepgramClient(API_KEY)

#         with open(audio_file, "rb") as file:
#             buffer_data = file.read()

#         payload: FileSource = {
#             "buffer": buffer_data,
#         }

#         #STEP 2: Configure Deepgram options for audio analysis
#         options = PrerecordedOptions(
#             model="nova-2",
#             smart_format=True,
#         )

#         # STEP 3: Call the transcribe_file method with the text payload and options
#         response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
#         transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
#         return(transcript)
    

#     except Exception as e:
#         print(f"Exception: {e}")


# if __name__ == "__main__":
#     print(speech2text('output.wav'))
