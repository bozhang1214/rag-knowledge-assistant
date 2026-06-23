import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL
from typing import List, Dict, Any, Tuple

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        # 加载 embedding 模型
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """批量添加文档块到向量库"""
        ids = [chunk["id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        embeddings = self.embedder.encode(texts, normalize_embeddings=True).tolist()
        
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """检索最相似的 k 个文档块"""
        query_embedding = self.embedder.encode([query], normalize_embeddings=True).tolist()[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        # 结果整理
        docs = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []
        
        sources = []
        for doc, meta, dist in zip(docs, metadatas, distances):
            sources.append({
                "filename": meta.get("source", "unknown"),
                "chunk": doc,
                "score": 1 - dist  # 余弦距离转换为相似度
            })
        return sources

    def delete_by_filename(self, filename: str) -> int:
        """删除指定文件的所有块，返回删除数量"""
        # 获取该文件的所有 ID
        results = self.collection.get(where={"source": filename})
        ids = results["ids"] if results else []
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档及其块数"""
        # 获取所有元数据
        results = self.collection.get(include=["metadatas"])
        if not results or not results["metadatas"]:
            return []
        # 统计每个文件的数量
        count_map = {}
        for meta in results["metadatas"]:
            src = meta.get("source", "unknown")
            count_map[src] = count_map.get(src, 0) + 1
        return [{"filename": k, "chunk_count": v} for k, v in count_map.items()]
