def format_documents(documents) -> str:   #把 Document 里面的文字拿出来，把多段文字合并成一段
    contents = []
    for document in documents:
        content = document.page_content
        contents.append(content)
    context = "\n\n".join(contents)
    return context