import os
from dotenv import load_dotenv
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field # for validation
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI


class ConfigLoader: #custom class that wraps around the dictionary returned by load_config
    def __init__(self):
        print(f"Loaded config.....")
        self.config = load_config() #Read the YAML file and return a dictionary.    
    
    def __getitem__(self, key): #allows an instance of class to be indexed using square brackets ([]), exactly like a Python dictionary
        return self.config[key]

class ModelLoader(BaseModel): #pydantic class for model loading
    model_provider: Literal["groq", "google"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None: #Pydantic models handle validation and initialization, automatic startup routine # load config after initializationn that we have written in .yaml file
        self.config = ConfigLoader() 
    
    # class Config:
    #     arbitrary_types_allowed = True  
    
    def load_llm(self):
        """
        Load and return the LLM model.
        """
        print("LLM loading...")
        print(f"Loading model from provider: {self.model_provider}")
        if self.model_provider == "groq":
            print("Loading LLM from Groq..............")
            groq_api_key = os.getenv("GROQ_API_KEY")
            # LOOK HERE: Because of __getitem__ in ConfigLoader, we can use brackets 
            # directly on self.config like a normal dictionary
            model_name = self.config["llm"]["groq"]["model_name"]
            llm=ChatGroq(model=model_name, api_key=groq_api_key)
        elif self.model_provider == "google":
            print("Loading LLM from google..............")
            google_api_key = os.getenv("GOOGLE_API_KEY")
            model_name = self.config["llm"]["google"]["model_name"]
            llm = ChatGoogleGenerativeAI(model=model_name, api_key=google_api_key)
        
        return llm
    