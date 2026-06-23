'use client';

import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceCard from './SourceCard';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: any[];
    tokens?: any;
}

export default function ChatArea({ className }: { className?: string }) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>(''); // 初始为空
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // 客户端挂载后读取 localStorage
    useEffect(() => {
        let saved = localStorage.getItem('rag_session_id');
        if (!saved) {
            saved = crypto.randomUUID();
            localStorage.setItem('rag_session_id', saved);
        }
        setSessionId(saved);
    }, []);

    // 当 sessionId 变化时写入 localStorage
    useEffect(() => {
        if (sessionId) {
            localStorage.setItem('rag_session_id', sessionId);
        }
    }, [sessionId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async () => {
        const question = input.trim();
        if (!question || loading) return;

        // 确保有 sessionId
        let currentSessionId = sessionId;
        if (!currentSessionId) {
            currentSessionId = crypto.randomUUID();
            setSessionId(currentSessionId);
        }

        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: question }]);
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, session_id: currentSessionId }),
            });
            if (!res.ok) {
                const err = await res.text();
                throw new Error(err || '请求失败');
            }
            const data = await res.json();
            setMessages(prev => [
                ...prev,
                {
                    role: 'assistant',
                    content: data.answer,
                    sources: data.sources,
                    tokens: data.tokens,
                },
            ]);
        } catch (err: any) {
            toast.error(err.message || '请求失败');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`flex flex-col ${className || ''}`}>
            <div className="flex-1 overflow-y-auto p-4 bg-white rounded-lg shadow-sm">
                {messages.length === 0 && (
                    <div className="text-center text-gray-400 mt-20">开始提问吧</div>
                )}
                {messages.map((msg, idx) => (
                    <div key={idx} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                        <div
                            className={`inline-block max-w-2xl p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-800'
                                }`}
                        >
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                        </div>
                        {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                            <div className="mt-2">
                                <details className="text-xs text-gray-500 cursor-pointer">
                                    <summary>📎 引用来源 ({msg.sources.length})</summary>
                                    <div className="mt-1 space-y-1">
                                        {msg.sources.map((src, i) => (
                                            <SourceCard key={i} source={src} />
                                        ))}
                                    </div>
                                </details>
                            </div>
                        )}
                        {msg.role === 'assistant' && msg.tokens && (
                            <div className="text-xs text-gray-400 mt-1">
                                Token: 输入 {msg.tokens.prompt_tokens} + 嵌入 {msg.tokens.embedding_tokens} / 输出 {msg.tokens.completion_tokens} / 总计 {msg.tokens.total_tokens}
                            </div>
                        )}
                    </div>
                ))}
                {loading && <div className="text-gray-500 text-sm">正在思考...</div>}
                <div ref={messagesEndRef} />
            </div>
            <div className="mt-4 flex">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="输入问题..."
                    className="flex-1 border rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                />
                <button
                    onClick={sendMessage}
                    disabled={loading || !input.trim()}
                    className="bg-blue-500 text-white px-6 py-2 rounded-r-lg hover:bg-blue-600 disabled:bg-gray-400"
                >
                    发送
                </button>
            </div>
        </div>
    );
}