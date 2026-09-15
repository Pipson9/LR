from langchain_chroma import Chroma
from utils.get_embedding_model import get_embedding_model

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "knowledge_base"


def search(query: str, category: str | None = None) -> None:
    embedding_model = get_embedding_model()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIR,
    )

    filter_condition = {"category": category} if category else None

    results = vector_store.similarity_search_with_score(
        query=query,
        k=3,
        filter=filter_condition,
    )

    print(f"\n用户问题：{query}")
    print("检索结果：")

    for index, (document, score) in enumerate(results, start=1):
        print("-" * 60)
        print(f"序号：{index}")
        print(f"距离分数：{score}")
        print(f"文件：{document.metadata.get('file_name')}")
        print(f"分类：{document.metadata.get('category')}")
        print(f"页码：{document.metadata.get('page', '无')}")
        print(f"内容：{document.page_content}")


def main() -> None:
    search("快递已经发出还能退款吗？")
    search("每个月可以补卡几次？", category="hr")


if __name__ == "__main__":
    main()