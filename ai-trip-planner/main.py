# from fastapi import FastAPI
# from pydantic import BaseModel
# from agent.agentic_workflow import GraphBuilder
# from fastapi.responses import JSONResponse
# import os

# app=FastAPI()

# class QueryRequest(BaseModel):
#     query: str


# # this is a post query, we'll post something through our form, it will come to the server then backend and then return a response
# @app.post("/query") # this route will be calling below func. this url is taking a query, so whenever we send a post request to this url, it will take the query and pass it to the agentic workflow
# async def query_travel_agent(query:QueryRequest): #taking query from user end
#     try:
#         print(query)
#         graph = GraphBuilder(model_provider="groq") # creating graph object, inside this func we will be calling the graph builder class from agentic workflow
#         react_app=graph() # calling the graph object as function, it then calls __call__ method of graph builder class, which in turn calls build_graph method and returns the graph object

#         #saving the graph
#         png_graph = react_app.get_graph().draw_mermaid_png()
#         with open("my_graph.png", "wb") as f:
#             f.write(png_graph)

#         print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        
#         # Assuming request is a pydantic object like: {"question": "your text"}, validating here
#         messages={"messages": [query.query]} # getting query from state
        
#         output = react_app.invoke(messages)

#         # If result is dict with messages:
#         if isinstance(output, dict) and "messages" in output:
#             final_output = output["messages"][-1].content  # Last AI response
#         else:
#             final_output = str(output)
        
#         return {"answer": final_output}
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})
    
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from agent.agentic_workflow import GraphBuilder
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Define the structure for individual chat messages
class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    messages: List[Message]  # Now accepts the full list of conversation messages

@app.post("/query")
async def query_travel_agent(request: QueryRequest):
    try:
        graph = GraphBuilder(model_provider="groq")
        react_app = graph()

        # Convert Pydantic message objects into the format LangGraph expects
        # LangGraph typically expects a list of message dicts or LangChain message objects
        formatted_messages = []
        for msg in request.messages:
            if msg.role == "user":
                formatted_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                formatted_messages.append(AIMessage(content=msg.content))

        input_data = {"messages": formatted_messages}
        output = react_app.invoke(input_data)
        # Extract the last AI response
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)
        
        return {"answer": final_output}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})