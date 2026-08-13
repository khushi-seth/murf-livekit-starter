import json
import logging
import uuid

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

from memory import (
    get_user,
    save_user,
    init_database,
    start_call,
    end_call,
)


logger = logging.getLogger("agent")

load_dotenv(".env.local")

init_database()


SYSTEM_PROMPT = """
You are a friendly and efficient Financial Services voice assistant.

Help users understand financial schemes, eligibility, and general
financial information.

You are a voice AI assistant. Be helpful, concise, natural, and honest.
Never pretend that you performed an action when you did not.


SUCCESS RULE:

A successful call means the caller successfully receives useful
financial information or completes a financial request.

Examples:

1. The caller receives financial information.
2. The caller completes an eligibility enquiry.
3. The caller receives a document list.
4. The caller successfully completes a currency conversion.
5. The caller successfully creates a human-help request.

After successfully completing the caller's request, use the
mark_call_success tool when appropriate.

Do not invent financial information.


CURRENCY TOOL:

- Use convert_currency for currency conversion requests.
- Never guess exchange rates.
- Always mention the date of the available exchange rate.
- If the service fails, tell the caller honestly.
- Never invent a rate.


MEMORY RULES:

- At the beginning of every conversation, use lookup_user.
- If the caller is known, greet them by name.
- If the caller is new, politely ask for their name.
- Never claim to remember something unless lookup_user returned it.
- Before saving personal information, ask for permission.
- Only save information after the caller clearly agrees.
- Never save Aadhaar numbers, PAN numbers, bank account numbers,
  card numbers, OTPs, passwords, UPI PINs, or other financial credentials.
- Do not invent memories.


HUMAN ESCALATION:

- Escalate when the caller reports possible fraud,
  unauthorized transactions, suspicious account activity,
  or explicitly asks for a human.
- Ask for explicit permission before creating a support request.
- If the caller says yes, call escalate_to_human.
- If the caller says no, do not call the tool.
- Never claim that a human has already contacted the caller.
- Never claim that an issue has already been resolved.


LANGUAGE:

- Reply in the language used by the caller.
- If the caller speaks Hindi, reply in Hindi.
- Hindi must be written in Devanagari script.
- Do not write Hindi using Roman/English letters.
"""


class Assistant(Agent):

    def __init__(
        self,
        user_id: str,
        call_id: int,
    ) -> None:

        self.user_id = user_id
        self.call_id = call_id

        # Day 8 call tracking
        self.call_success = False

        super().__init__(
            instructions=SYSTEM_PROMPT
        )


    @function_tool
    async def mark_call_success(
        self,
        context: RunContext,
    ) -> str:

        """Mark the current call as successful."""

        self.call_success = True

        logger.info(
            f"CALL MARKED SUCCESS | call_id={self.call_id}"
        )

        return "The call has been marked as successful."


    @function_tool
    async def lookup_user(
        self,
        context: RunContext,
    ) -> str:

        """Look up the current caller in memory."""

        logger.info(
            f"Looking up caller: {self.user_id}"
        )

        user = get_user(
            self.user_id
        )

        if user is None:

            logger.info(
                "No saved user found."
            )

            return (
                "No saved information exists for this caller."
            )

        logger.info(
            f"Found saved user: {user['name']}"
        )

        return json.dumps(
            user
        )


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
            f"Saving approved memory for {self.user_id}"
        )

        try:

            try:

                parsed_facts = json.loads(
                    facts
                )

                if not isinstance(
                    parsed_facts,
                    dict,
                ):

                    parsed_facts = {
                        "memory": str(
                            parsed_facts
                        )
                    }

            except (
                json.JSONDecodeError,
                TypeError,
            ):

                parsed_facts = {
                    "memory": facts
                }


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


            facts_text = json.dumps(
                parsed_facts
            ).lower()


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

            return (
                "I could not save that information."
            )


    @function_tool
    async def convert_currency(
        self,
        context: RunContext,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> str:

        """Convert currencies using latest available exchange-rate data."""

        from_currency = (
            from_currency
            .upper()
            .strip()
        )

        to_currency = (
            to_currency
            .upper()
            .strip()
        )


        if amount < 0:

            raise ToolError(
                "The amount must be zero or greater."
            )


        if (
            len(from_currency) != 3
            or len(to_currency) != 3
        ):

            raise ToolError(
                "Please use three-letter currency codes such as USD or INR."
            )


        try:

            url = (
                "https://api.frankfurter.app/latest"
                f"?from={from_currency}"
                f"&to={to_currency}"
            )


            session = (
                utils.http_context.http_session()
            )


            async with session.get(
                url,
                timeout=10,
            ) as response:

                if response.status != 200:

                    raise ToolError(
                        "I couldn't reach the exchange-rate service right now."
                    )

                data = await response.json()


            rates = data.get(
                "rates",
                {},
            )

            rate = rates.get(
                to_currency
            )

            rate_date = data.get(
                "date",
                "unknown date",
            )


            if rate is None:

                raise ToolError(
                    f"I couldn't find an exchange rate for "
                    f"{from_currency} to {to_currency}."
                )


            rate = float(
                rate
            )

            converted_amount = (
                amount * rate
            )


            logger.info(
                f"Currency conversion: "
                f"{amount} {from_currency} = "
                f"{converted_amount} {to_currency} "
                f"using rate from {rate_date}"
            )


            # Successful financial request
            self.call_success = True


            return (
                f"Latest available exchange rate from "
                f"{rate_date}: "
                f"1 {from_currency} = "
                f"{rate:.4f} {to_currency}. "
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
                "I don't want to guess the rate."
            )


    @function_tool
    async def escalate_to_human(
        self,
        context: RunContext,
        reason: str,
    ) -> str:

        """Create a human support request after permission."""

        reference_id = (
            f"FIN-{str(uuid.uuid4())[:4].upper()}"
        )


        logger.info(
            f"Human escalation created | "
            f"Reference ID: {reference_id} | "
            f"Caller: {self.user_id} | "
            f"Reason: {reason}"
        )


        # A successfully created human-help request
        # is a successful call outcome.
        self.call_success = True


        return (
            f"Human support request created successfully. "
            f"Your reference ID is {reference_id}. "
            f"A financial support representative can review your case."
        )


server = AgentServer()


def prewarm(
    proc: JobProcess,
):

    proc.userdata["vad"] = (
        silero.VAD.load()
    )


server.setup_fnc = prewarm


@server.rtc_session(
    agent_name="my-agent"
)
async def my_agent(
    ctx: JobContext,
):

    ctx.log_context_fields = {
        "room": ctx.room.name,
    }


    # Connect to LiveKit room
    await ctx.connect()


    # Wait for caller
    participant = (
        await ctx.wait_for_participant()
    )


    user_id = (
        participant.identity
    )


    # ============================================
    # DAY 8 — START CALL TRACKING
    # ============================================

    channel = (
        "sip"
        if participant.kind
        == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
        else "browser"
    )


    call_id = start_call(
        channel=channel
    )


    logger.info(
        f"CALL STARTED | "
        f"call_id={call_id} | "
        f"channel={channel}"
    )


    logger.info(
        f"Caller joined: identity={user_id}"
    )


    # ============================================
    # CREATE AGENT SESSION
    # ============================================

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


    # ============================================
    # CREATE ASSISTANT
    # ============================================

    agent = Assistant(
        user_id=user_id,
        call_id=call_id,
    )


    # ============================================
    # START VOICE SESSION
    # ============================================

    await session.start(

        agent=agent,

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


    # ============================================
    # DAY 8 — SUCCESS
    # ============================================

    # session.start() completed successfully,
    # so the voice agent successfully connected
    # and started handling the caller.

    agent.call_success = True


    # IMPORTANT:
    # Save SUCCESS immediately instead of waiting
    # for the shutdown callback.

    end_call(
        call_id=call_id,
        outcome="success",
    )


    logger.info(
        f"DAY8 CALL SUCCESS | "
        f"call_id={call_id}"
    )


    # ============================================
    # OPTIONAL SHUTDOWN LOG
    # ============================================

    async def on_shutdown():

        logger.info(
            f"DAY8 CALL ENDED | "
            f"call_id={call_id}"
        )


    ctx.add_shutdown_callback(
        on_shutdown
    )


if __name__ == "__main__":

    cli.run_app(
        server
    )