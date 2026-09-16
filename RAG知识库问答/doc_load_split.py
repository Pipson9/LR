from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader,Docx2txtLoader

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


TYPE={".txt",".md",".pdf"}

#1根据文件类型加载文件
def load_file(filepath: Path, base_dir: Path):
    list1 = filepath.rglob("*")
    all_documents = []
    for file in list1:
        suffix= file.suffix.lower()      #lower()转小写
        #根据不同类型创建不同的加载器对象loader()
        #此时   loader的类型：<class 'langchain_community.document_loaders.text.TextLoader'>
        if suffix in {".txt",".md"}:
            loader=TextLoader(           #如果是txt类型用TextLoader
                file_path=str(file),
                encoding="utf-8",
            )
        elif suffix in {".pdf"}:
            loader=PyPDFLoader(             #如果是pdf类型用PyPDFLoader
                file_path=str(file),
            )
        elif suffix in {".docx"}:
            loader=Docx2txtLoader(            #如果是docx类型用Docx2txtLoader
                file_path=str(file)
            )
        else:
            continue
        documents=loader.load()
        category = file.parent.relative_to(base_dir).as_posix()
        for doc in documents:
            doc.metadata["category"] = category
            doc.metadata['file_name'] = file.name
            doc.metadata['file_type'] = suffix
        all_documents.extend(documents)

        #调用加载器的 load() 方法，读取文件，并把读取结果保存到 documents 变量中。
    return all_documents                     #此时documents是list[] 他里面是document对象，

                                                # document对象里面是page_content和metadata

def split_documents(document:list[Document]):
    rcts = RecursiveCharacterTextSplitter(    #创建一个切割器对象 rcts
    chunk_size= 100,
    chunk_overlap=20,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    add_start_index=True                   # 切割文本时，把每个 chunk 在原始文档中的起始位置记录下来，放入 Document 的 metadata 里面。
                                           # 简单理解：
                                            #告诉你：这一小段文字原来在大文档的哪个位置。

    )
    chunks = rcts.split_documents(document)
    # 调用文本切割器对象 rcts的 split_documents() 方法，把 documents 切割成多个文本块。

    for index,chunk in enumerate(chunks):
         chunk.metadata['chunk_id']=index
    return chunks
