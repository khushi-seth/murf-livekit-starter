import os

from fastapi import FastAPI
from fastapi.responses import Response
from livekit import api
from dotenv import load_dotenv

load_dotenv(".env.local")

app = FastAPI()


@app.post("/twiml")
async def twiml():
    lkapi = api.LiveKitAPI()

    response = await lkapi.connector.connect_twilio_call(
        api.ConnectTwilioCallRequest(
            twilio_call_direction=
            api.ConnectTwilioCallRequest.TWILIO_CALL_DIRECTION_OUTBOUND,

            room_name="finassist-outbound-call",

            participant_identity="financial-user",

            participant_name="Financial Services User",

            destination_country="IN",

            agents=[
                api.RoomAgentDispatch(
                    agent_name="my-agent"
                )
            ],
        )
    )

    connect_url = response.connect_url

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{connect_url}" />
    </Connect>
</Response>
"""

    await lkapi.aclose()

    return Response(
        content=twiml_response,
        media_type="application/xml"
    )