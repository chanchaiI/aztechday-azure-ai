import os
import streamlit as st
import time
from audiorecorder import audiorecorder
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from threading import Thread

speech_key = os.getenv("AZURE_SPEECH_KEY", "")
service_region = os.getenv("AZURE_SERVICE_REGION", "")
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-US-AmberNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

openaiEndpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT_URL", "")
openaiKey = os.getenv("AZURE_OPEN_AI_KEY", "")
deployment = os.getenv("AZURE_AI_DEPLOYMENT_NAME", "")
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "")
search_key = os.getenv("AZURE_SEARCH_KEY", "")
embedding_endpoint = os.getenv("AZURE_AI_EMBEDDING_ENDPOINT", "")
embedding_key = os.getenv("AZURE_AI_EMBEDDING_KEY", "")

client = AzureOpenAI(
    azure_endpoint=openaiEndpoint,
    api_key= openaiKey,
    api_version="2024-05-01-preview",
)

def textToSpeech(text):
    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

def recognize_from_microphone():
    # audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    audio_config = speechsdk.audio.AudioConfig(filename="audio.wav")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
        st.markdown(speech_recognition_result.text)
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

# Streamed response emulator
def response_generator(prompt):
    completion = client.chat.completions.create(
        model=deployment,
        messages= [
        {
          "role": "user",
          "content": f"{prompt}"
        }],
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False,
        extra_body={
          "data_sources": [{
              "type": "azure_search",
              "parameters": {
                "filter": None,
                "endpoint": f"{search_endpoint}",
                "index_name": "ai-build-techday-v1",
                "semantic_configuration": "azureml-default",
                "authentication": {
                  "type": "api_key",
                  "key": f"{search_key}"
                },
                "embedding_dependency": {
                  "type": "endpoint",
                  "endpoint": f"{embedding_endpoint}",
                  "authentication": {
                    "type": "api_key",
                    "key": f"{embedding_key}"
                  }
                },
                "query_type": "vector",
                "in_scope": True,
                "role_information": "You are an AI assistant that helps people find information named Ava from ABCompany.",
                "strictness": 3,
                "top_n_documents": 5
              }
            }]
        }
    )
    print(completion.to_json())
    response = completion.choices[0].message.content

    return response

def write_stream(text):
    for i in range(len(text)):
        yield text[i]
        time.sleep(0.05)

def main():
    st.title("Simple chat")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    audio = audiorecorder("Click to record", "Click to stop recording")

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        submitPrompt(prompt)
        
    elif len(audio) > 0:
        st.audio(audio.export().read())
        audio.export("audio.wav", format="wav")

        audio_config = speechsdk.audio.AudioConfig(filename="audio.wav")
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            prompt = speech_recognition_result.text
            print("Recognized: {}".format(speech_recognition_result.text))
            submitPrompt(prompt)

        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

def submitPrompt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        chatResponse = response_generator(prompt)
        Thread(target=textToSpeech, args=(chatResponse,)).start()
        response = st.write_stream(write_stream(chatResponse))

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

main()


