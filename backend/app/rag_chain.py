import json
import tiktoken
from openai import OpenAI
from app.config import DEEPSEEK_API_KEY, LLM_MODEL, TOP_K
from app.vector_store import VectorStore
from app.utils import count_tokens

class RAGChain:
    def __init__(self):
        self.vector_store = VectorStore()
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        self.token_encoder = tiktoken.get_encoding("cl100k_base")  # 用于估算

    def ask(self, question: str, session_id: str = None) -> dict:
        # 1. 检索相关文档块
        sources = self.vector_store.search(question, k=TOP_K)
        
        # 2. 构建上下文
        context_parts = []
        for idx, src in enumerate(sources, 1):
            context_parts.append(f"[{idx}] (文件名: {src['filename']})\n{src['chunk']}")
        context = "\n\n".join(context_parts)
        
        # 3. 构建 prompt
        prompt = f"""你是一个知识库问答助手。请根据以下上下文回答用户的问题。
如果上下文不足以回答问题，请如实告知，不要编造信息。

上下文：
{context}

用户问题：{question}

回答："""
        
        # 4. 调用 LLM
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的知识库问答助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        answer = response.choices[0].message.content
        
        # 5. 计算 token
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        
        # 6. 估算 embedding token（由于 embedding 模型本地运行，无法精确统计，此处估算）
        # 实际生产可使用 API 式 embedding 获取精确值
        embedding_tokens = count_tokens(question) + sum(count_tokens(src['chunk']) for src in sources)
        
        tokens = {
            "embedding_tokens": embedding_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens + embedding_tokens
        }
        
        return {
            "answer": answer,
            "sources": sources,
            "tokens": tokens
        }
