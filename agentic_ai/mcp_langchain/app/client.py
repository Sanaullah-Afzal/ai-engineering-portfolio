from langchain_mcp_adapters.client import MultiServerMCPClient # shoudl be multiserver
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
groq_api_key = os.getenv("GROQ_API_KEY")


async def main():
    client = MultiServerMCPClient( #client interacting witb these servers
        { # client key value pair
            "math":{ # first server so this client will be able to interact with mcpserver
                "command": "python", # command use to run server, could br uv
                "args": ["mathserver.py"], # file mame with complete path
                "transport": "stdio", # running on normal command line with I/O
            },

            "weather":{
                "url": "http://localhost:8000/mcp", # /mcp where will be finding the entire mcp running
                "transport": "streamable-http",     # url so we using Http

            }
        }
    )

    tools = await client.get_tools() #getting info of both above tools line 12 
    model=ChatGroq(model="openai/gpt-oss-120b")
    agent=create_agent(
        model,tools
    )

    #invoke this agent with what message we give
    math_response = await agent.ainvoke(
        {"messages":{"role": "user", "content":"what is (3+5) * 2 ?"}}
    )

    print("Math response:", math_response["messages"][-1].content)


    weather_response = await agent.ainvoke(
        {"messages":{"role": "user", "content":"what is the weather in Abbottabad ?"}}
    )

    print("Weather response:", weather_response["messages"][-1].content)

asyncio.run(main()) #whenever we define func that async, it is run with this command/library