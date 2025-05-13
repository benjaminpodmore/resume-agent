from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os


load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

async def main():
    llm = ChatOllama(model="qwen3:30b-a3b", base_url=OLLAMA_BASE_URL)

    async with MultiServerMCPClient(
        {
            "tavily": {
                "command": "npx",
                "args": ["-y", "tavily-mcp"],
                "env": {"TAVILY_API_KEY": TAVILY_API_KEY}
            }
        }
    ) as client:
        tavily_agent = create_react_agent(model=llm, tools=client.get_tools(), prompt="You are a internet-powered bot with search tools to find answers.", name="internet_agent")

        supervisor_agent = create_supervisor(model=llm, agents=[tavily_agent], prompt="You manage one agent, an internet-search agent.").compile()

        user_input = input("Enter a message: ")

        state = await supervisor_agent.ainvoke({"messages": [{"role": "user", "content": user_input}]})

        print(state)
        print(state["messages"][-1].content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())