import os
import uuid
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )

    def load_document(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """加载并解析文档，返回文档列表（每个元素包含 page_content 和 metadata）"""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            # 为每个页面添加元数据
            for doc in docs:
                doc.metadata["source"] = filename
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
        else:
            raise ValueError(f"不支持的文件类型: {ext}")
        return docs

    def split_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将文档切分为块，并添加 chunk_index 和唯一 id"""
        chunks = self.splitter.split_documents(docs)
        result = []
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = idx
            chunk.metadata["id"] = str(uuid.uuid4())
            result.append({
                "id": chunk.metadata["id"],
                "text": chunk.page_content,
                "metadata": chunk.metadata
            })
        return result
