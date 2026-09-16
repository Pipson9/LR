from rag_service import RAGService


def print_sources(sources: list[dict]) -> None:
    if not sources:
        print("资料来源：无")
        return

    print("\n资料来源：")

    for index, source in enumerate(sources, start=1):
        source_text = source["file_name"]

        if source["page"] is not None:
            source_text += f"，第 {source['page']} 页"

        if source["category"]:
            source_text += f"，分类：{source['category']}"

        print(f"{index}. {source_text}")


def main() -> None:
    rag_service = RAGService()

    print("企业知识库助手已启动，输入 exit 退出。")

    while True:
        question = input("\n请输入问题：").strip()

        if question.lower() == "exit":
            print("程序已退出。")
            break

        if not question:
            print("问题不能为空。")
            continue

        try:
            result = rag_service.ask(question)
            print(f"\n回答：{result['answer']}")
            print_sources(result["sources"])
        except Exception as error:
            print(f"处理失败：{error}")


if __name__ == "__main__":
    main()