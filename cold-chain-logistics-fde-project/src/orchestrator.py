import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver # save in langgraph

# ==========================================
# 1. SETUP & PATH RESOLUTION
# ==========================================
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

from src.agent_tools import query_telemetry_db, fetch_corridor_conditions, search_compliance_sop

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] # add_messages to keeep on adding message to the list      

# ==========================================
# 2. FACTORY INITIALIZATION: AGENT REASONER LLM
# ==========================================

AGENT_LLM_SETTING = os.getenv("Agent_llm", "OLLAMA").strip().upper()

if AGENT_LLM_SETTING == "OPENROUTER":
    print("🤖 Brain Mode: Utilizing Cloud OpenRouter Reasoner (gpt-4o)...")
    from langchain_openai import ChatOpenAI

    # llm = ChatOpenAI(
    #     # model="nvidia/nemotron-3.5-lightning:free",
    #     model="openrouter/free",  # Automatically routes to active free models supporting tools & orchestration
    #     temperature=0,            # 0 means deterministic output for strict tool argument generation
    #     openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    #     # base_url="https://openrouter.ai/api/v1/chat/completions", gives error
    #     base_url="https://openrouter.ai/api/v1", # required otherwise routes to openai
    #     max_tokens=2048,
    # )

    llm = ChatOpenAI(
        # model="nvidia/nemotron-3.5-lightning:free",
        model="gemini-3.8-flash",
        temperature=0,            # 0 means deterministic output for strict tool argument generation
        openai_api_key=os.getenv("GOOGLE_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        max_tokens=2048,
    )

elif AGENT_LLM_SETTING == "GROQ":
    print("⚡ Brain Mode: Utilizing Groq via OpenAI-Compatible API...")
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model="openai/gpt-oss-safeguard-20b",  # Fast, highly capable open model on Groq supporting tools
        temperature=0,                    # 0 for strict, deterministic tool arguments
        openai_api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",  # Groq's official OpenAI-compatible endpoint
        max_tokens=2048,
    )

elif AGENT_LLM_SETTING == "GOOGLE":
    print("🐳 Brain Mode: Utilizing Flagship DeepSeek Cloud Reasoner (deepseek-v4-pro)...")
    from langchain_google_genai import ChatGoogleGenerativeAI
    # from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
    )

else:  # FALLBACK / DEFAULT RUNNER MODE
    print("🤗 Brain Mode: Local Fallback Activated. Binding Local Ollama (qwen2.5:7b)...")
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="qwen2.5:7b", temperature=0, num_predict=1024)

fde_tools = [query_telemetry_db, fetch_corridor_conditions, search_compliance_sop]
llm_with_tools = llm.bind_tools(fde_tools)

# ==========================================
# 3. GRAPH ARCHITECTURE ASSEMBLY
# ==========================================
def reasoning_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"]) # messages from user
    return {"messages": [response]}

print("⚙️ Compiling LangGraph FDE Orchestrator...")
graph_builder = StateGraph(AgentState)
graph_builder.add_node("reasoner", reasoning_node)
graph_builder.add_node("tools", ToolNode(fde_tools))

graph_builder.add_edge(START, "reasoner")
graph_builder.add_conditional_edges("reasoner", tools_condition)
graph_builder.add_edge("tools", "reasoner")

fde_agent = graph_builder.compile(checkpointer=MemorySaver()) # have access to agent_tools

# ==========================================
# 4. CHAT LOOP TESTING PANEL
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*55)
    print("🚀 FDE Supply Chain Orchestrator State Machine Online")
    print(f"   Configured Execution: [LLM: {AGENT_LLM_SETTING}] -> [Embeddings: {os.getenv('Embeddings_model', 'LOCAL')}]")
    print("="*55 + "\n")
    
    # Load the business-structured system prompt from the external file
    prompt_path = project_root / "src" / "prompts" / "system_prompt.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_instructions = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {prompt_path}")
        system_instructions = "You are a helpful AI assistant." # Basic fallback

    system_prompt = SystemMessage(content=system_instructions)

    # 💡 THE FIX: Provide an initial user message alongside the system prompt 
    # so Google's backend always receives valid 'contents'.
    initial_user_msg = HumanMessage(content="System initialized. Ready for operations.")

    # each thread will have its own memory thats maintained in this
    thread_config = {"configurable": {"thread_id": "production_test_1"}}
    fde_agent.invoke({"messages": [system_prompt,initial_user_msg]}, config=thread_config)
    
    
    while True: # it is a react agent so using it in a loop
        user_input = input("\nDispatcher > ")
        if user_input.lower() in ['exit', 'quit']:
            break # to break out of the loop
            
        events = fde_agent.stream({"messages": [("user", user_input)]}, config=thread_config, stream_mode="updates")
        for event in events:
            for node_name, node_state in event.items():
                if node_name == "tools":
                    print("   [System] 🔄 Retrieving external data elements via ToolNode...")
                elif node_name == "reasoner":
                    latest_msg = node_state["messages"][-1]

                    # Extract text whether content is a string or a list of blocks
                    if isinstance(latest_msg.content, list):
                        text_content = "".join([block.get("text", "") for block in latest_msg.content if isinstance(block, dict)])
                    else:
                        text_content = latest_msg.content

                    if latest_msg.content:
                        print(f"\n🤖 FDE Agent:\n{latest_msg.content}")