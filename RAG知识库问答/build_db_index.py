from doc_load_split import load_file,split_documents
from utils.get_embedding_model import get_embedding_model
from langchain_chroma import Chroma
from pathlib import Path
#知识库目录
DIR= Path("knowledge_base")

# Chroma保存位置
PERSIST_DIR= "chroma_db"

# 集合名称，类似数据库表名
COLLECTION_NAME= "knowledge_base"

def main ():
    #1加载所有文件
    documents=load_file(DIR,DIR)

    # 2.数据切分
    chunks=split_documents(documents)

    # 3.创建向量数据库
    vector_store =Chroma(
        embedding_function=get_embedding_model(), #embedding模型，把文本转换为向量
        persist_directory=PERSIST_DIR,              # 向量数据库保存目录
        collection_name=COLLECTION_NAME,             # 集合名称，类似数据库表名
        collection_metadata={"hnsw:space":"cosine"}  #cosine:余弦相似度
    )

    # 4添加数据
    ids = [f"chunk-{chunk.metadata['chunk_id']}" for chunk in chunks]

    # ids = []
    # for chunk in chunks:
    #     chunk_id = chunk.metadata["chunk_id"]
    #     id = f"chunk-{chunk_id}"
    #     ids.append(id)

    vector_store.add_documents(documents=chunks, ids=ids)

    print("\n===== 构建完成 =====")
    print(f"原始文档数量：{len(documents)}")
    print(f"文档块数量：{len(chunks)}")
    print(f"向量库目录：{PERSIST_DIR}")
    print(f"集合名称：{COLLECTION_NAME}")


if __name__ == "__main__":
    main()