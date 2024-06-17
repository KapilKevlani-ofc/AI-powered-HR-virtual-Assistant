# AI-powered HR Virtual Assistant
This project is a virtual voice-to-voice assistant designed to interact with users through voice input. It leverages a combination of technologies to convert voice input to text, process the text using a Large Language Model (LLM) integrated with Retrieval-Augmented Generation (RAG) on ChromaDB, and then convert the text output back to voice.
## Project Overview
The AI-powered HR Virtual Assistant follows a multi-step process to handle user interactions:
1. **Voice Input**: The user speaks into the microphone.
2. **Speech-to-Text Conversion**: The voice input is converted to text using a speech recognition system.
3. **Text Processing**: The text is fed into an LLM integrated with RAG on ChromaDB to generate a relevant response.
4. **Text-to-Speech Conversion**: The generated text response is converted back to voice output.
5. **Voice Output**: The system plays the voice output to the user.
## Project Structure
The project is organized into several key components, each responsible for a specific part of the workflow. Below is a detailed explanation of each component and the corresponding files.

### 1. Data Ingestion
- **File**: `data_ingestion.py`
- **Description**: This module is present in src/components and is designed to load available data which is in the form of pdf. The module used here can take multiple pdfs as well as a single pdf.


### 2. Data Transformation
- **File**: `data_transformation.py`
- **Description**: This module is present in src/components and is designed to convert the large texts present in pdfs to chunks of size 500 and overlapping of 20 tokens using Langchain's recursive_character_text_splitter.



### 3. Database Creation
- **File**: `database_management.py`
- **Description**: This module is present in src/components and is designed to create a vector_store(DB) which is stored in local memory instead of any cloud platform. This module ensures that if a database is already created, it will use that database instead of creating a new one else it will create a new one if it don't find a database. This module returns a retriver so that the database can be fetched for similarity search.



### 4. Voice Input
- **File**: `SpeechtoText.py`
- **Description**: This module is present in src/pipelines and it captures the user's voice input using a microphone with the help of DEEPGRAM's API and convert the recorded audio file into text. It combines the short transcripts of user voice and provides the full sentence.

### 5. Text Processing with LLM and RAG
- **File**: `language_model_processor.py`
- **Description**: This module is present in src/pipelines and it uses 'mixtral-8x7b-32768' LLM with chatgroq's API for faster responses. This module sends the text input to an LLM integrated with RAG on ChromaDB to generate a relevant response.


### 6. Text-to-Speech Conversion
- **File**: `texttospeech.py`
- **Description**: This module is present in src/pipelines and it converts the text response from the LLM into a voice output using a Deepgram's API for low latency and high accuracy transcript conversions.


### 7. End Point
- **File**: `application.py`
- **Description**: This module acts as an endpoint to the project and it combines all available modules to process the incoming voice query to text and then back to voice. Here a simple streamlit fronted is created which consists of buttons like start conversation and end conversation. Whenever a user says "Goodbye" the whole conversation history will appear to the user on frontend and once the end conversation button is pressed then the chatbot is available again for a new session.
- **Function**: `play_voice_output(audio_file)`

To get started with the project, follow these steps:
1. **Clone the Repository**:
  ```bash
  git clone
https://github.com/KapilKevlani-ofc/AI-powered-HR-virtual-Assistant.git
  cd AI-powered-HR-virtual-Assistant
  ```
2. **Install Dependencies**:
  ```
  pip install -r requirements.txt
  ```
3. **Run the Application**:
  ```
  streamlit run application.py
  ```
## Configuration
- **Deepgram API**: Configure your Deepgram API keys and settings in `.env`. A ".env_example" file is there you can check it out and define the names and keys as per it.
- **LLM API**: Ensure your Chatgroq configurations are set in `.env`.
