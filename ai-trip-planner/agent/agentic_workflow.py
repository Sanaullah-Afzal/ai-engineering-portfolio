
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import PlaceSearchTool
from tools.expense_calculator_tool import CalculatorTool
from tools.currency_conversion_tool import CurrencyConverterTool

class GraphBuilder():
    def __init__(self,model_provider: str = "groq"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        self.tools = []
        
        self.weather_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConverterTool()
        
        self.tools.extend([* self.weather_tools.weather_tool_list, 
                           * self.place_search_tools.place_search_tool_list,
                           * self.calculator_tools.calculator_tool_list,
                           * self.currency_converter_tools.currency_converter_tool_list])
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        
        self.system_prompt = SYSTEM_PROMPT
    
    
    def agent_function(self,state: MessagesState): # supervisor which takes decision on which tool to use based on the user input and the system prompt
        """Main agent function"""
        user_question = state["messages"] 
        input_question = [self.system_prompt] + user_question
        response = self.llm_with_tools.invoke(input_question)
        return {"messages": [response]}

#this is langgraph workflow. from where this graph_builder is going to be called? we ll create endpoint in main.py to call it
    def build_graph(self):
        graph_builder=StateGraph(MessagesState) # input to each node through message state only, graph builder is a state graph object
        graph_builder.add_node("agent",self.agent_function)
        graph_builder.add_node("tools",ToolNode(tools=self.tools))       
        graph_builder.add_edge(START,"agent")
        graph_builder.add_conditional_edges("agent",tools_condition) # whether to go to tools or end based on the agent's response, if the agent's response is a tool call, it will go to tools node, else it will go to end node
        graph_builder.add_edge("tools","agent")
        graph_builder.add_edge("agent",END)
        self.graph = graph_builder.compile()
        return self.graph
        
    def __call__(self): #automatically called build_graph when we call the graph object as a function, so that we don't have to call build_graph explicitly
        return self.build_graph()