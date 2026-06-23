'use client';

import { useEffect, useState } from 'react';
import ChatArea from './components/ChatArea';
import DocumentList from './components/DocumentList';
import UploadArea from './components/UploadArea';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '';

export default function Home() {
    const [documents, setDocuments] = useState([]);
    const [refreshKey, setRefreshKey] = useState(0);

    const refreshDocuments = () => {
        setRefreshKey(prev => prev + 1);
    };

    useEffect(() => {
        const fetchDocs = async () => {
            try {
                const res = await fetch(`${API_BASE}/documents`);
                if (res.ok) {
                    const data = await res.json();
                    setDocuments(data);
                }
            } catch (err) {
                console.error('获取文档列表失败', err);
            }
        };
        fetchDocs();
    }, [refreshKey]);

    return (
        <div className="flex h-screen bg-gray-50">
            {/* 左侧：文档管理 */}
            <div className="w-1/3 p-6 border-r bg-white overflow-y-auto">
                <h2 className="text-xl font-bold mb-4">📚 知识库</h2>
                <UploadArea onUploadSuccess={refreshDocuments} />
                <DocumentList documents={documents} onDelete={refreshDocuments} />
            </div>
            {/* 右侧：问答区 */}
            <div className="flex-1 flex flex-col p-6">
                <h2 className="text-xl font-bold mb-4">💬 问答</h2>
                <ChatArea className="flex-1" />
            </div>
        </div>
    );
}
