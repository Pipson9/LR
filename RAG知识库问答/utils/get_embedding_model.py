import os

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

# 本地 embedding 模型路径。默认按项目根目录下的 models/ 查找，
# 也可以通过 .env 中的 EMBEDDING_MODEL_PATH 指定绝对路径，例如：
#   EMBEDDING_MODEL_PATH=D:\models\bge-small-zh-v1.5
DEFAULT_EMBEDDING_MODEL = "models/bge-small-zh-v1.5"


def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL_PATH", DEFAULT_EMBEDDING_MODEL),
        model_kwargs={"device": os.getenv("EMBEDDING_DEVICE", "cpu")},
        encode_kwargs={"normalize_embeddings": True}  # l2 归一化
    )
    return embedding_model
