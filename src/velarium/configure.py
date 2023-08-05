# Standard Packages
from functools import partial
from collections import defaultdict

# External Packages
from fastapi import FastAPI
from asgiref.sync import sync_to_async
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory

# Internal Packages
from velarium.db.models import Conversation

from django.contrib.auth.models import User

import logging

logger = logging.getLogger(__name__)

def initialize_agent() -> LLMChain:
    "Initialize the Conversational Chain with Memory"
    llm = ChatOpenAI(temperature=0)
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                f"""
    You are Khoj, a friendly, smart and helpful personal assistant.
    Use your general knowledge and our past conversations to provide assistance.
    """.strip()
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
    )
    converse = partial(LLMChain, llm=llm, prompt=prompt, verbose=True)
    return converse


def initialize_conversation_sessions() -> defaultdict[str, ConversationBufferMemory]:
    "Initialize the Conversation Sessions"
    logger.info("Initializing Conversation Sessions")
    conversation_sessions = defaultdict(lambda: ConversationBufferMemory(memory_key="chat_history", return_messages=True))
    users = User.objects.all()
    for user in users:
        conversations = Conversation.objects.filter(user=user)[:10]
        conversations = conversations[::-1]
        # Reconstruct the conversation sessions from the database
        for conversation in conversations:
            conversation_sessions[conversation.user.khojuser.uuid].chat_memory.add_user_message(conversation.user_message)
            conversation_sessions[conversation.user.khojuser.uuid].chat_memory.add_ai_message(conversation.bot_message)

    return conversation_sessions
    
async def save_conversation(user, message, response):
    "Save the conversation to the database"
    await sync_to_async(Conversation.objects.create)(user=user, user_message=message, bot_message=response)


def configure_routes(app: FastAPI):
    "Configure the API Routes"
    logger.info("Including routes")
    from velarium.routers.api import api

    app.include_router(api, prefix="/api")
