from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AppState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str | None
    name: str | None
    email: str | None
    platform: str | None
