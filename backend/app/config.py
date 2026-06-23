import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")  # 可选

# 向量库持久化目录
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "knowledge_base"

# 分块参数
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# 检索参数
TOP_K = 4

# Embedding 模型（使用 DeepSeek 的 Embedding 接口，若不支持则改本地）
# 注意：DeepSeek 目前不提供官方 embedding API，改为使用 OpenAI 兼容方式或本地
# 这里我们使用 sentence-transformers 本地模型，在启动时加载
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"   # 本地模型

# DeepSeek Chat 模型
LLM_MODEL = "deepseek-v4-flash"

# 文件上传限制
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
