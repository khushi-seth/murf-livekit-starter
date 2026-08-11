
import asyncio
import os

from dotenv import load_dotenv
from livekit import api
from twilio.rest import Client

load_dotenv(".env.local")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")

ROOM_NAME = "finassist-outbound-call"


async def main():
    print("Creating LiveKit Twilio connector session...")

    lkapi = api.LiveKitAPI()

    try:
        response = await lkapi.connector.connect_twilio_call(
            api.ConnectTwilioCallRequest(
                twilio_call_direction=(
                    api.ConnectTwilioCallRequest.TWILIO_CALL_DIRECTION_OUTBOUND
                ),
                room_name=ROOM_NAME,
                participant_identity="financial-user",
                participant_name="Financial Services User",
                agents=[
                    api.RoomAgentDispatch(
                        agent_name="my-agent"
                    )
                ],
            )
        )

        connect_url = response.connect_url

        print("LiveKit connector created.")
        print("CONNECT URL:", connect_url)

        twiml_url = connect_url.replace("wss://", "https://")

        print("TWIML URL:", twiml_url)
        print("Starting Twilio call...")

        twilio_client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        call = twilio_client.calls.create(
            from_=TWILIO_FROM_NUMBER,
            to=TO_NUMBER,
            url=twiml_url,
            method="POST"
        )

        print("CALL STARTED SUCCESSFULLY!")
        print("CALL SID:", call.sid)
        print("CALL URL:", twiml_url)

        await asyncio.sleep(10)

    finally:
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(main())

