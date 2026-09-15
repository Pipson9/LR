
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
def get_model(temperature:float):
    model =init_chat_model(
        model="qwen-turbo" ,
        model_provider="openai",
        api_key=os.getenv("BAILIAN_APIKEY"),
        base_url=os.getenv("BAILIAN_BASE_URL"),
    )
    return model
