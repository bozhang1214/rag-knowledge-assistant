import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """估算文本的 token 数"""
    return len(encoder.encode(text))
