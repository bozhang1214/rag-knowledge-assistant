import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models import UploadResponse, DocumentInfo, AskRequest, AskResponse, Source
from app.document_processor import DocumentProcessor
from app.vector_store import VectorStore
from app.rag_chain import RAGChain
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

app = FastAPI(title="知识库问答助手 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
processor = DocumentProcessor()
vector_store = VectorStore()
rag_chain = RAGChain()

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传文档并建立向量索引"""
    # 检查文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件类型，仅支持 {', '.join(ALLOWED_EXTENSIONS)}")
    
    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"文件大小超过 {MAX_FILE_SIZE//1024//1024}MB 限制")
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # 加载并分块
        docs = processor.load_document(tmp_path, file.filename)
        chunks = processor.split_documents(docs)
        # 存入向量库
        vector_store.add_documents(chunks)
        return UploadResponse(
            filename=file.filename,
            chunk_count=len(chunks),
            message=f"成功上传并索引 {len(chunks)} 个文本块"
        )
    except Exception as e:
        raise HTTPException(500, f"处理文档失败: {str(e)}")
    finally:
        os.unlink(tmp_path)

@app.get("/documents", response_model=list[DocumentInfo])
async def list_documents():
    """获取已上传文档列表"""
    return vector_store.list_documents()

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """删除指定文档及其所有向量块"""
    deleted = vector_store.delete_by_filename(filename)
    return {"message": f"已删除文档 '{filename}'，共移除 {deleted} 个向量块"}

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """RAG 问答"""
    result = rag_chain.ask(request.question, request.session_id)
    return AskResponse(
        answer=result["answer"],
        sources=[Source(**s) for s in result["sources"]],
        tokens=result["tokens"]
    )

@app.get("/health")
async def health():
    return {"status": "ok", "chunks": vector_store.collection.count()}
