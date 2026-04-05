import os, sys
from typing import List, Tuple, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
import json
import http.client
from src.config.config import settings
from src.exceptions.custom_exception import AgentException


@tool
def google_serperapi_search(query: str) -> str:
    """Searches the web for information using SerperAPI."""

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
      "q": "apple inc"
    })
    headers = {
      'X-API-KEY': settings.SERPER_API_KEY,
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")

def skin_disease_agent(model: str) -> Optional[AgentExecutor]:


    try:
        llm = ChatGroq(
        temperature=0,
        model_name=model, 
        api_key=os.environ['GROQ_API_KEY']  
        )

        tools = [google_serperapi_search]

        system_prompt = (
            "You are DermaCareNet-AI, a helpful dermatology assistant. "
            "Use available tools to search for reliable medical sources. "
            "Always base your responses on current dermatological guidelines."
        )
        human_prompt = (
            "Analyze the following detected skin condition: {detected_conditions}. "
            "Gather relevant information using the search tool. Then summarize:\n"
            "1. Condition overview\n"
            "2. Common causes\n"
            "3. Hygiene and prevention tips\n"
            "4. Diet recommendations\n"
            "5. Over-the-counter or natural treatments\n"
            "6. Complications if untreated\n"
            "7. When to consult a dermatologist.\n"
            "Make sure to cite brief context from the search results."
        )
        prompt_0 = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(
            llm, 
            tools, 
            prompt_0
        )
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,
            handle_parsing_errors=True
        )
        return agent_executor
    except Exception as e:
        raise AgentException(
            message=''
        )