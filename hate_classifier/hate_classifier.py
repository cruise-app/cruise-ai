from fastapi import FastAPI
from pydantic import BaseModel
import arabic_reshaper
from bidi.algorithm import get_display
from dotenv import dotenv_values
from google import genai
from notificationapi_python_server_sdk import notificationapi
# import requests

secrets = dotenv_values(".env")

client = genai.Client(api_key=secrets["Gemini_API_KEY"])

notificationapi.init(
    secrets["NOTIFICATIONS_ID"],
    secrets["NOTIFICATIONS_API_KEY"],
    'https://api.eu.notificationapi.com'
)

app = FastAPI()

class payload(BaseModel):
    trip_id: str
    transcript: str
    user_id: str

# To test the health of the API
@app.get("/")
async def root():
    return {"hate_classifier": "200 OK"}

# To classify the hateful/curse words in the transcript
@app.post("/classify")
async def classify_transcript(payload: payload):
    input = payload.model_dump()
    text = input["transcript"]
    trip_id = input["trip_id"]
    user_id = input["user_id"]

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
        
        # map_link = f"https://google.com"
        # alert_text = f"Hello this is CRUISE's AI hate detector\n\nYour trusted contact is sending alerts to you\n\nTranscript: {get_display(arabic_reshaper.reshape(text))}\n{map_link}"
        
        # alert_response = requests.post(f"https://api.callmebot.com/whatsapp.php?phone=201069885999&text={alert_text}&apikey=4567627")
        # print("Alert sent")
        
        alert_response = await send_alert(text, trip_id, user_id)
    
    return response

@app.post("/send-alert")
async def send_alert(text: str, trip_id: str, user_id: str):
    

    try:
        # Send alert using NotificationAPI
        response = await notificationapi.send({
            "type": "alert",
            "to": {
                "email": "alihisham26m@gmail.com",
                "number": "+201069885999"
            },
            "parameters": {
                "name": "Shahd",
                "transcript": get_display(arabic_reshaper.reshape(text)),
                "map_link": f"https://ali26m.github.io/security-project/?user_id={user_id}",
            }
        })
        print("NotificationAPI response:", response)
    
    except Exception as e:
        print("Alert failed:", e)
    
    return {"status": "Alert sent"}

# Command run: uvicorn hate_classifier:app --port 5000 --reload