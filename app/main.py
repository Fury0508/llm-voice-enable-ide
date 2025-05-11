import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from graph import create_chat_graph
from dotenv import load_dotenv
import asyncio
from openai.helpers import LocalAudioPlayer
from openai import AsyncOpenAI
import os 
openai = AsyncOpenAI()
load_dotenv()
MONGODB_URI = "mongodb://admin:admin@localhost:27017"

config = {"configurable":{"thread_id":"2"}}


async def speak(text: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input="Today is a wonderful day to build something people love!",
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)
def main():
     with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer = checkpointer)
        r = sr.Recognizer()

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            r.pause_threshold = 2
            while True:
                print("Say something!")
                audio = r.listen(source)


                print("Processing audio...")
                sst = r.recognize_google(audio)

                print("You said: ",sst)

                for event in graph.stream({"messages": [{"role":"user","content": sst}]},config,stream_mode="values"):
                    if "messages" in event:
                        event["messages"][-1].pretty_print()
                        latest_message = event["messages"][-1]
                
                if latest_message.content is not None:
                        # Speak the latest message
                        asyncio.run(speak(latest_message.content))




main()

