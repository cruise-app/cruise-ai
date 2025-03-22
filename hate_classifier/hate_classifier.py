from fastapi import FastAPI
from pydantic import BaseModel
import arabic_reshaper
from bidi.algorithm import get_display
from dotenv import dotenv_values
from google import genai
import cohere

secrets = dotenv_values(".env")

client = genai.Client(api_key=secrets["Gemini_API_KEY"])
co = cohere.ClientV2(api_key=secrets["COHERE_API_KEY"])

app = FastAPI()

class Transcript(BaseModel):
    transcript: str

# To test the health of the API
@app.get("/")
async def root():
    return {"message": "200 OK"}

# To classify the hateful/curse words in the transcript
@app.post("/classify")
async def classify_transcript(input: Transcript):
    data = input.model_dump()
    text = data["transcript"]

    # print(get_display(arabic_reshaper.reshape(text)))
    print(text)

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        # contents = f"Is \"{text}\" a hateful/curse word in Egyptian Arabic? Answer with 1 (Yes) or 0 (No)"
        contents = f"هل \"{get_display(arabic_reshaper.reshape(text))}\" كلمة كراهية أو شتيمة باللهجة المصرية؟ أجب بـ 1 (نعم) أو 0 (لا)"
    )

    response_co = co.chat(
    model="command-r-plus-08-2024",
    messages=[{"role": "user",
               "content": f"هل \"{get_display(arabic_reshaper.reshape(text))}\" كلمة كراهية أو شتيمة باللهجة المصرية؟ أجب بـ 1 (نعم) أو 0 (لا)" 
            #    "content": f"Is \"{get_display(arabic_reshaper.reshape(text))}\" a hateful/curse word in Egyptian Arabic? Answer with 1 (Yes) or 0 (No)"
               }],
)

    print("from gemini: ", response.text)
    
    print("from cohere: ", response_co.message.content[0].text)

# Command run: uvicorn hate_classifier:app --reload