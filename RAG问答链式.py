from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from utils.get_embedding_model import get_embedding_model
from utils.get_model import  get_model
from utils.fromat_documents import format_documents
from RAG问答非链式 import prompt_template

model = get_model(temperature=0.3)
# 1.连接向量数据库
vector_store= Chroma(
    collection_name="knowledge_base",
    embedding_function=get_embedding_model(),  #这里时加载,连接向量数据库，不是创建
    persist_directory="chroma_db",
)

#2创建检索对象retriever，把向量数据库对象vector转换为检索器对象retriever ，设置返回三个最相近的结果
retriever= vector_store.as_retriever(
    search_kwargs={"k": 3}
)
rag_chain=(
    {"context":retriever | format_documents,
     "question":RunnablePassthrough(),
    }
    |prompt_template | model | StrOutputParser()
)
answer=rag_chain.invoke("创建")
print(answer)

#
# 用户输入 "question"    y
#
#         ↓
#
# {
#  "context": retriever | format_documents,
#  "question": RunnablePassthrough()
# }
#
#         ↓
#
# retriever
#         ↓
# format_documents
#
#         +
# RunnablePassthrough
#
#         ↓
#
# {
#  context,
#  question
# }
#
#         ↓
#
# prompt_template
#
#         ↓
#
# model
#
#         ↓
#
# StrOutputParser()
#
#         ↓
#
# answer