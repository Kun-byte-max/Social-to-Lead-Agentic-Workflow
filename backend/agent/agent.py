import os
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from state.state import AppState
from rag.rag import retrieve_knowledge
from tools.mock_lead import mock_lead_capture

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)

def get_text_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
    return str(content)

def classify_intent(state: AppState):
    last_msg = get_text_content(state["messages"][-1].content)
    prompt = f"Classify this user message into ONE of: GREETING, INFORMATION, HIGH_INTENT.\nMessage: '{last_msg}'\nRespond ONLY with the classification word."
    
    if state.get("intent") == "HIGH_INTENT" and not (state.get("name") and state.get("email") and state.get("platform")):
        intent = "HIGH_INTENT"
    else:
        ans = get_text_content(llm.invoke(prompt).content).strip().upper()
        if "GREETING" in ans:
            intent = "GREETING"
        elif "HIGH_INTENT" in ans or "HIGH INTENT" in ans:
            intent = "HIGH_INTENT"
        else:
            intent = "INFORMATION"
            
    return {"intent": intent}

def extract_fields(state: AppState):
    if state["intent"] == "HIGH_INTENT":
        last_msg = get_text_content(state["messages"][-1].content)
        prompt = f"""Extract Name, Email, and Platform from this message if present. 
        Only extract if the user explicitly provided it.
        Message: "{last_msg}"
        Format exactly as:
        NAME: [name or None]
        EMAIL: [email or None]
        PLATFORM: [platform or None]
        """
        ans = get_text_content(llm.invoke(prompt).content)
        updates = {}
        for line in ans.split('\n'):
            if line.startswith("NAME:") and "None" not in line:
                name = line.replace("NAME:", "").strip()
                if name: updates["name"] = name
            elif line.startswith("EMAIL:") and "None" not in line:
                email = line.replace("EMAIL:", "").strip()
                if email.lower() != "none": updates["email"] = email
            elif line.startswith("PLATFORM:") and "None" not in line:
                plat = line.replace("PLATFORM:", "").strip()
                if plat.lower() != "none": updates["platform"] = plat
        
        # Merge with existing state
        for key in ["name", "email", "platform"]:
            if key not in updates and state.get(key):
                updates[key] = state[key]
                
        return updates
    return {}

def route_after_extract(state: AppState):
    if state["intent"] == "HIGH_INTENT":
        if state.get("name") and state.get("email") and state.get("platform"):
            return "tool_executor"
        return "lead_collector"
    elif state["intent"] == "GREETING":
         return "greeting"
    return "information"

def information_node(state: AppState):
    query = get_text_content(state["messages"][-1].content)
    chunks = retrieve_knowledge(query)
    context = "\n".join(chunks)
    
    sys = f"You are AutoStream AI Sales Assistant. Answer the user strictly using this context:\n{context}\nKeep answers concise and helpful."
    resp = llm.invoke([SystemMessage(content=sys)] + state["messages"])
    return {"messages": [resp]}

def greeting_node(state: AppState):
    sys = "You are the AutoStream AI Sales Assistant. The user just greeted you. Respond politely and ask how you can help with our SaaS product."
    resp = llm.invoke([SystemMessage(content=sys)] + state["messages"])
    return {"messages": [resp]}

def lead_collector_node(state: AppState):
    sys_prompt = f"""You are the AutoStream AI Sales Assistant. The user wants to subscribe or buy our product.
    We must collect their Name, Email, and Creator Platform (like YouTube, Instagram).
    Currently we have:
    Name: {state.get('name') or 'Missing'}
    Email: {state.get('email') or 'Missing'}
    Platform: {state.get('platform') or 'Missing'}
    
    Ask for EXACTLY ONE missing field politely. Keep it conversational and natural."""
    
    resp = llm.invoke([SystemMessage(content=sys_prompt)] + state["messages"])
    return {"messages": [resp]}

def tool_executor(state: AppState):
    result = mock_lead_capture(state)
    msg = AIMessage(content=result["msg"])
    if result["success"]:
        return {"messages": [msg], "intent": None, "name": None, "email": None, "platform": None}
    else:
        warning_msg = AIMessage(content=result["msg"] + " Could you please provide it again correctly?")
        if "email" in result["msg"].lower():
             return {"messages": [warning_msg], "email": None}
        return {"messages": [warning_msg]}

builder = StateGraph(AppState)
builder.add_node("classify", classify_intent)
builder.add_node("extract", extract_fields)
builder.add_node("greeting", greeting_node)
builder.add_node("information", information_node)
builder.add_node("lead_collector", lead_collector_node)
builder.add_node("tool_executor", tool_executor)

builder.add_edge(START, "classify")
builder.add_edge("classify", "extract")
builder.add_conditional_edges("extract", route_after_extract, {
  "greeting": "greeting",
  "information": "information",
  "lead_collector": "lead_collector",
  "tool_executor": "tool_executor"
})
builder.add_edge("greeting", END)
builder.add_edge("information", END)
builder.add_edge("lead_collector", END)
builder.add_edge("tool_executor", END)

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
agent = builder.compile(checkpointer=memory)
