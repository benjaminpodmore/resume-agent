from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

async def main():
    llm = ChatOllama(model="llama3.2:3b-instruct-q4_K_M", base_url=OLLAMA_BASE_URL)

    async with MultiServerMCPClient(
        {
            "tavily": {
                "command": "npx",
                "args": ["-y", "tavily-mcp"],
                "env": {"TAVILY_API_KEY": TAVILY_API_KEY}
            }
        }
    ) as client:
        agent = create_react_agent(llm, tools=client.get_tools(), prompt="You are a internet-powered bot with search tools to find answers.")

        response = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "How do I use docker-compose to create containers for python development?"}
            ]
        })
        print(response)
        for m in response["messages"]:
            m.pretty_print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())