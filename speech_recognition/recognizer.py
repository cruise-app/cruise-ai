# # some speech to text alternatives:
# # https://portal.speechmatics.com/settings/api-keyss
# # https://arabot.io/en
# # https://tryhamsa.com/

from speechmatics.batch_client import BatchClient
from speechmatics.models import ConnectionSettings
from httpx import HTTPStatusError
import requests
import arabic_reshaper
from bidi.algorithm import get_display
from dotenv import dotenv_values
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form
import shutil
import os
import traceback
from supabase import create_client
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()

# Get secrets
secrets = dotenv_values(".env")
PATH_TO_FILE = "audio_input/ride_partition.mp3"

def aggregate_and_format(msg):

    buffer = []    # Temporary buffer the words until a full sentence is formed
    # Reshape Arabic text for proper display. convert to RTL format (get_display)
    rtl_text = get_display(arabic_reshaper.reshape(msg))

    buffer.append(rtl_text)

    # Reverse the buffer to get the correct order of the words
    # and join the words to form a sentence
    transcript_text = " ".join(buffer[::-1])
    
    buffer.clear()

    return transcript_text


# Configure Speechmatics connection settings and parameters
settings = ConnectionSettings(
    url=secrets["SPEECHMATICS_CONNECTION_URL"],
    auth_token=secrets["SPEECHMATICS_API_KEY"],
)
conf = {
    "type": "transcription",
    "transcription_config": {
        "language": "ar"
    }
}

# Initialize Supabase client
supabase = create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_API_KEY"])

# Initialize MongoDB client
mongo_client = MongoClient(
    secrets["MONGODB_URL"],
    server_api=ServerApi('1')
)
collection = mongo_client['cruise-ai']['hate-detections']


@app.get("/")
async def root():
    return {"recognizer": "200 OK"}

@app.post("/transcript-audio/")
async def transcript_audio(file: UploadFile = File(...), trip_id: str = Form(...), user_id: str = Form(...)):
    try:

        print("Received file:", file.filename)
        print("Trip ID:", trip_id)
        print("User ID:", user_id)

        # Save the uploaded file
        file_location = f"audio_input/ride_partition.mp3"
        os.makedirs("audio_input", exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"File saved to {file_location}")

        # Begin transcription
        with BatchClient(settings) as client:
            try:
                job_id = client.submit_job(audio=PATH_TO_FILE, transcription_config=conf)
                print(f'job {job_id} submitted to Speechmatics')

                transcript = client.wait_for_completion(job_id, transcription_format='txt')

                rtl_transcript = aggregate_and_format(transcript)
                print(rtl_transcript)

            except HTTPStatusError as e:
                if e.response.status_code == 401:
                    print('Invalid API key')
                elif e.response.status_code == 400:
                    print(e.response.json()['detail'])
                else:
                    raise e
            except Exception as e:
                print(f'An error occurred: {e}')
                traceback.print_exc()
            finally:
                client.close()
                
        # Send the transcript to the classifier
        hate_response = requests.post(
            "http://127.0.0.1:5000/classify", 
            json={"transcript": rtl_transcript, 
                   "trip_id": trip_id, 
                   "user_id": user_id}
            )
        print("Hate classification response:", hate_response.json())
        
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Store the audio into Supabase
        with open("audio_input/ride_partition.mp3", "rb") as f:
            
            sb_response = (
                supabase.storage
                .from_("ride-audio-bucket")
                .upload(
                    file = f,
                    path = f"trip_{trip_id}/ride_partition_{time_stamp}.mp3",
                    file_options = {"upsert": "false"}
                )
            )
        print("Audio uploaded to:", sb_response.path)

        # Get the public URL of the uploaded audio
        audio_url = (
            supabase.storage
            .from_("ride-audio-bucket")
            .create_signed_url(
                f"trip_{trip_id}/ride_partition_{time_stamp}.mp3",
                604800
            )
        )
        print("Got audio public URL")
        
        # Store metadata in MongoDB
        metadata = {
            "trip_id": trip_id,
            "transcript": get_display(arabic_reshaper.reshape(rtl_transcript)),
            "hate_classification": hate_response.json(),
            "audio_url": audio_url["signedURL"],
            "timestamp": datetime.now().isoformat()
        }
        collection.insert_one(metadata)
        print("Metadata stored in MongoDB")
    
    except Exception as e:
        traceback.print_exc()
        
    finally:
        # Delete up the uploaded audio
        if os.path.exists(file_location):
            os.remove(file_location)
            
# uvicorn recognizer:app --port 8000 --reload