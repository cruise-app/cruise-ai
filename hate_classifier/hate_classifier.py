from fastapi import FastAPI
from pydantic import BaseModel
import cohere
import arabic_reshaper
from bidi.algorithm import get_display
from dotenv import dotenv_values
 
secrets = dotenv_values(".env")

co = cohere.ClientV2(api_key=secrets["COHERE_API_KEY"])

app = FastAPI()

class Transcript(BaseModel):
    transcript: str

@app.get("/")
async def root():
    return {"message": "200 OK"}

@app.post("/classify")
async def classify_transcript(input: Transcript):
    data = input.model_dump()
    text = data["transcript"]

    # text = get_display(arabic_reshaper.reshape(text))
    print(text)
    
    res = co.chat(
        model="command-a-03-2025",
        messages=[
            {
                "role": "user",
                "content": f"Is \"{text}\" a swear word? Reply with 1 (Yes) or 0 (No) only"
            }
        ],
    )

    # print(f"Classify: {text}\nHate speech/swear word? Reply with 1 (Yes) or 0 (No) only")
    print(res.message.content[0].text)

    return res.message.content[0].text

# Command run: uvicorn hate_classifier:app --reload