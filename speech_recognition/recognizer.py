# some speech to text alternatives:
# https://portal.speechmatics.com/settings/api-keyss
# https://arabot.io/en
# https://tryhamsa.com/

import speechmatics
from httpx import HTTPStatusError
import requests
from urllib.request import urlopen
import sys
import json
import arabic_reshaper
from bidi.algorithm import get_display
from dotenv import dotenv_values
from datetime import datetime
import yt_dlp

# Get API key
secrets = dotenv_values(".env")

# The raw input audio stream
# it will be a few seconds ahead of the actual Video
# youtube_url = "https://youtu.be/0b5DWgZNifQ" # non hate.  elshater
# youtube_url = "https://youtu.be/DSUrjFF85J4" # non hate. legends
youtube_url = "https://www.youtube.com/watch?v=jucMfhKJ0uY" # hate. bahgat saber

def get_audio_stream(youtube_url):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return urlopen(info['url']) if 'url' in info else None

full_transcript = []
buffer = []  # Temporary buffer the words until a full sentence is formed

def convert_to_RTL(msg):

    # Extract transcript text
    transcript_text = msg["metadata"]["transcript"]

    # Reshape Arabic text for proper display. convert to RTL format (get_display)
    rtl_text = get_display(arabic_reshaper.reshape(transcript_text))

    buffer.append(rtl_text)

    # Check if the current transcript contains a ending punctuation (check if the sentence is completed)
    if any(punct in rtl_text for punct in ['.', '؟', '!', '…']):

        # Reverse the buffer to get the correct order of the words
        # and join the words to form a sentence
        transcripted_text = " ".join(buffer[::-1])

        # Add timestamp
        timed_transcripted_text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {" ".join(buffer[::-1])}"

        # Print transcript with timestamp
        print(timed_transcripted_text)

        # Append transcript with timestamp to list
        full_transcript.append(timed_transcripted_text)

        # Clear the buffer for the next sentence
        buffer.clear()

        return transcripted_text

def send_transcript_to_classifier(transcript):

    # Convert to RTL format and send to classifier
    timed_transcripted_text = convert_to_RTL(transcript)

    # Send the transcript to the classifier. 
    # If the transcript is None, this means the sentence is not completed yet. So will not send it
    if timed_transcripted_text is not None:

        try:
            response = requests.post("http://127.0.0.1:8000/classify", json={"transcript": timed_transcripted_text})
        except requests.exceptions.RequestException as e:
            print(e)

# Create a transcription client
ws = speechmatics.client.WebsocketClient(
    speechmatics.models.ConnectionSettings(
        url=secrets["SPEECHMATICS_CONNECTION_URL"],
        auth_token=secrets["SPEECHMATICS_API_KEY"],
    )
)

# Register the event handler for full transcript
ws.add_event_handler(
    event_name=speechmatics.models.ServerMessageType.AddTranscript,
    event_handler=send_transcript_to_classifier,
)

settings = speechmatics.models.AudioSettings()

# Define transcription parameters
conf = speechmatics.models.TranscriptionConfig(
    language="ar",
    enable_partials=True,
    max_delay=5,
    enable_entities=True
)

try:
    ws.run_synchronously(get_audio_stream(youtube_url), conf, settings)
except KeyboardInterrupt:

    with open("Full_Transcript.txt", "w", encoding="utf-8") as f:

        for text in full_transcript:
            # Apply reshaper and RTL formatting
            rtl_text = get_display(arabic_reshaper.reshape(text)) 
            f.write(rtl_text + "\n")

except HTTPStatusError as e:

    if e.response.status_code == 401:
        print('Invalid API key - Check your API_KEY at the top of the code!')
    else:
        raise e
