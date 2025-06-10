from fastapi import FastAPI
from pydantic import BaseModel
import arabic_reshaper
from bidi.algorithm import get_display
from dotenv import dotenv_values
from google import genai
import requests

secrets = dotenv_values(".env")

client = genai.Client(api_key=secrets["Gemini_API_KEY"])

app = FastAPI()

class Transcript(BaseModel):
    trip_id: str
    transcript: str

# To test the health of the API
@app.get("/")
async def root():
    return {"hate_classifier": "200 OK"}

# To classify the hateful/curse words in the transcript
@app.post("/classify")
async def classify_transcript(input: Transcript):
    data = input.model_dump()
    text = data["transcript"]
    trip_id = data["trip_id"]

    print(text)
    # print(get_display(arabic_reshaper.reshape(text)))

    # send the text to the Gemini API
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents = f"هل \"{get_display(arabic_reshaper.reshape(text))}\" كلمة كراهية أو شتيمة باللهجة المصرية؟ أجب بـ 1 (نعم) أو 0 (لا)"
    )
    
    response = response.text.strip()
    print("is hate: ", response)
    
    # Send alert if hate speech detected
    if response == "1":    
        
        map_link = f"https://google.com"
        alert_text = f"Hello this is CRUISE's AI hate detector\n\ىYour trusted contact is sending alerts to you\n\ىTranscript: {get_display(arabic_reshaper.reshape(text))}\n{map_link}"
        
        alert_response = requests.post(f"https://api.callmebot.com/whatsapp.php?phone=201069885999&text={alert_text}&apikey=4567627")
        print("Alert sent")
    
    return response

# Command run: uvicorn hate_classifier:app --port 5000 --reload