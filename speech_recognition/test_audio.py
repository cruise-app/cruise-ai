import requests

url = "http://127.0.0.1:8000/transcript-audio/"
audio_path = "test-bad.m4a"
audio_path = "demo.mp3"
# audio_path = "test.mp3"

with open(audio_path, "rb") as audio_file:
    files = {"file": (audio_path, audio_file, "audio/mpeg")}
    response = requests.post(url, files=files, data={"trip_id": "987", "user_id": "12345"})

print(response.json())
