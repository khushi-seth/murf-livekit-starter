
import json
import logging

from dotenv import load_dotenv
from livekit import rtc

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    tokenize,
    room_io,
    utils,
)

from livekit.agents.llm import ToolError

from livekit.plugins import (
    murf,
    silero,
    google,
    deepgram,
    noise_cancellation,
)

from livekit.plugins.turn_detector.multilingual import MultilingualModel

from memory import get_user, save_user, init_database


logger = logging.getLogger("agent")


load_dotenv(".env.local")

init_database()


SYSTEM_PROMPT = """
You are a friendly and efficient Financial Services voice assistant.

Help users understand financial schemes, eligibility, and general
financial information.

CURRENCY TOOL:

- You have a currency conversion tool called convert_currency.
- Use it whenever the caller asks for a current currency conversion
  or current exchange rate.
- Do not guess or invent exchange rates.
- The tool fetches the latest available exchange-rate data from
  an external financial data source.
- Always mention the date of the rate when giving the result.
- Speak the result naturally. Never read JSON, API fields, or
  technical information aloud.
- If the currency tool fails, clearly tell the caller that the
  exchange-rate service is temporarily unavailable.
- Never invent a rate when the data source is unavailable.

MEMORY RULES:

- At the beginning of every conversation, use the lookup_user tool.
- If the caller is known, greet them by name and use saved information.
- If the caller is new, politely ask for their name.
- Never claim to remember something unless the lookup_user tool returned it.
- Before saving personal information, explicitly ask for permission.
- Only save information after the caller clearly says yes.
- If the caller says no, do not save anything.
- Never save Aadhaar numbers, PAN numbers, bank account numbers,
  card numbers, OTPs, passwords, UPI PINs, or financial credentials.
- Only save useful information relevant to future conversations.
- Do not invent memories.

LANGUAGE & SCRIPT:

- Reply in the language used by the caller.
- If the caller speaks Hindi, reply in Hindi.
- Hindi must be written in Devanagari script.
- Do not write Hindi using Roman/English letters.
"""


class Assistant(Agent):

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id

        super().__init__(
            instructions=SYSTEM_PROMPT
        )

    @function_tool
    async def lookup_user(
        self,
        context: RunContext,
    ) -> str:
        """Look up the current caller in the memory database."""

        logger.info(
            f"Looking up caller: {self.user_id}"
        )

        user = get_user(self.user_id)

        if user is None:
            logger.info("No saved user found.")
            return "No saved information exists for this caller."

        logger.info(
            f"Found saved user: {user['name']}"
        )

        return json.dumps(user)


    @function_tool
    async def save_user_memory(
        self,
        context: RunContext,
        name: str,
        language_preference: str,
        facts: str,
    ) -> str:
        """Save caller information after explicit permission."""

        logger.info(
            f"Saving approved memory for caller: {self.user_id}"
        )

        try:

            # Try JSON first.
            try:
                parsed_facts = json.loads(facts)

                if not isinstance(parsed_facts, dict):
                    parsed_facts = {
                        "memory": str(parsed_facts)
                    }

            except (json.JSONDecodeError, TypeError):

                logger.warning(
                    "Facts were not valid JSON. Saving as plain text."
                )

                parsed_facts = {
                    "memory": facts
                }


            # Block sensitive financial information.
            sensitive_words = [
                "aadhaar",
                "aadhar",
                "pan number",
                "account number",
                "bank account",
                "card number",
                "credit card",
                "debit card",
                "otp",
                "password",
                "upi pin",
                "pin",
            ]

            facts_text = json.dumps(parsed_facts).lower()

            for word in sensitive_words:

                if word in facts_text:

                    logger.warning(
                        f"Blocked sensitive information: {word}"
                    )

                    return (
                        "I cannot save sensitive financial information."
                    )


            save_user(
                user_id=self.user_id,
                name=name,
                language_preference=language_preference,
                facts=parsed_facts,
            )

            logger.info(
                f"User memory saved successfully for {self.user_id}"
            )

            return (
                "The approved information has been saved successfully."
            )


        except Exception:

            logger.exception(
                "Failed to save user memory."
            )

            return "I could not save that information."


    @function_tool
    async def convert_currency(
        self,
        context: RunContext,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> str:
        """
        Convert money between currencies using the latest available
        exchange-rate data from an external financial data source.

        Use this tool whenever the user asks for a current currency
        conversion or exchange rate.

        Do not use this tool for investment advice, stock predictions,
        or historical exchange rates.

        Args:
            amount: Amount of money to convert.
            from_currency: Three-letter source currency code,
                such as USD or INR.
            to_currency: Three-letter target currency code,
                such as INR or USD.
        """

        from_currency = from_currency.upper().strip()
        to_currency = to_currency.upper().strip()


        if amount < 0:

            raise ToolError(
                "The amount must be zero or greater."
            )


        if len(from_currency) != 3 or len(to_currency) != 3:

            raise ToolError(
                "Please use three-letter currency codes such as USD or INR."
            )


        try:

            url = (
                "https://api.frankfurter.app/latest"
                f"?from={from_currency}"
                f"&to={to_currency}"
            )


            session = utils.http_context.http_session()


            async with session.get(
                url,
                timeout=10,
            ) as response:

                if response.status != 200:

                    raise ToolError(
                        "I couldn't reach the exchange-rate service right now."
                    )


                data = await response.json()


            rates = data.get("rates", {})

            rate = rates.get(to_currency)

            rate_date = data.get(
                "date",
                "unknown date"
            )


            if rate is None:

                raise ToolError(
                    f"I couldn't find an exchange rate for "
                    f"{from_currency} to {to_currency}."
                )


            rate = float(rate)

            converted_amount = amount * rate


            logger.info(
                f"Currency conversion: "
                f"{amount} {from_currency} = "
                f"{converted_amount} {to_currency} "
                f"using rate from {rate_date}"
            )


            return (
                f"Latest available exchange rate from {rate_date}: "
                f"1 {from_currency} = {rate:.4f} {to_currency}. "
                f"{amount:.2f} {from_currency} is approximately "
                f"{converted_amount:.2f} {to_currency}."
            )


        except ToolError:

            raise


        except Exception:

            logger.exception(
                "Currency conversion tool failed."
            )

            raise ToolError(
                "The exchange-rate service is temporarily unavailable. "
                "I don't want to guess the rate, so please try again shortly."
            )


server = AgentServer()


def prewarm(proc: JobProcess):

    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):

    ctx.log_context_fields = {
        "room": ctx.room.name,
    }


    await ctx.connect()


    participant = await ctx.wait_for_participant()


    user_id = participant.identity


    logger.info(
        f"Caller joined: identity={user_id}"
    )


    session = AgentSession(

        stt=deepgram.STT(
            model="nova-3",
        ),

        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),

        tts=murf.TTS(
            voice="Anisha",
            locale="en-IN",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=2
            ),
            text_pacing=True,
        ),

        turn_detection=MultilingualModel(),

        vad=ctx.proc.userdata["vad"],

        preemptive_generation=True,
    )


    await session.start(

        agent=Assistant(
            user_id=user_id
        ),

        room=ctx.room,

        room_options=room_io.RoomOptions(

            audio_input=room_io.AudioInputOptions(

                noise_cancellation=lambda params: (

                    noise_cancellation.BVCTelephony()

                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP

                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )


if __name__ == "__main__":

    cli.run_app(server)