import asyncio
from notificationapi_python_server_sdk import notificationapi
from dotenv import dotenv_values
secrets = dotenv_values(".env")

notificationapi.init(
    secrets["NOTIFICATIONS_ID"],
    secrets["NOTIFICATIONS_API_KEY"]
)

async def send_notification():
    response = await notificationapi.send({
        "type": "alert",
        "to": {
            "email": "alihisham26m@gmail.com",
            "number": "+201069885999"
        },
        "parameters": {
            "name": "Shahd",
            "transcript": "testComment",
            "map_link": "https://google.com"
}
    })
    print(response)
    
asyncio.run(send_notification())