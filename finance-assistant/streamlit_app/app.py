import streamlit as st
import aiohttp
from agents.voice_agent import speech_to_text
import os
import asyncio

st.title("Finance Assistant")

audio_file = st.file_uploader("Upload audio query", type=["wav", "mp3"])
query = st.text_input("Or type your query")

if st.button("Get Response"):
    if audio_file:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.read())
        query = speech_to_text("temp_audio.wav")
        st.write("Transcribed Query:", query)
    
    if query:
        async def fetch_response():
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8000/process_query", json={"query": query}) as resp:
                    return await resp.json()
        
        result = asyncio.run(fetch_response())
        st.write("Response:", result["narrative"])
        st.audio(result["audio_output"])