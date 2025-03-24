from curses.ascii import isdigit
from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents.llm.chat_context import ChatMessage
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import WELCOME_MESSAGE,INSTRUCTION
import logging
import os

logger =logging.getLogger("AI-Agent")
logger.setLevel(logging.INFO)
load_dotenv()

async def entrypoint(ctx: JobContext):
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting entrypoint")
    await ctx.connect(auto_subscribe= AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    model = openai.realtime.RealtimeModel(
        instructions="INSTRUCTION",
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"],
    )
    assistant_fnc = AssistantFnc()
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)
    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content = WELCOME_MESSAGE
        )
    )
    session.response.create()

    @session.on("user_speech_comitted")
    def on_user_speech_comitted(msg: llm.ChatMessage):
        if isinsatance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.C

        if assistant_fnc.get_user_profile():
            pass
        else:
            pass

    def find_profile(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="system",
                content=""
            )
        )
        session.response.create()

    def handle_query(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="user",
                content=msg.content
            )
        )
        session.response.create()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
