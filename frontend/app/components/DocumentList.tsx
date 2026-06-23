'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '';

export default function DocumentList({ documents, onDelete }: { documents: any[], onDelete: () => void }) {
    const [deleting, setDeleting] = useState<string | null>(null);

    const handleDelete = async (filename: string) => {
        if (!confirm(`确定要删除 "${filename}" 吗？`)) return;
        setDeleting(filename);
        try {
            const res = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, {
                method: 'DELETE',
            });
            if (res.ok) {
                toast.success('删除成功');
                onDelete();
            } else {
                toast.error('删除失败');
            }
        } catch (err) {
            toast.error('网络错误');
        } finally {
            setDeleting(null);
        }
    };

    if (documents.length === 0) {
        return <p className="text-gray-500 text-sm">暂无文档，请上传</p>;
    }

    return (
        <ul className="space-y-2">
            {documents.map((doc) => (
                <li key={doc.filename} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span className="text-sm truncate">{doc.filename}</span>
                    <span className="text-xs text-gray-500">{doc.chunk_count} 块</span>
                    <button
                        onClick={() => handleDelete(doc.filename)}
                        disabled={deleting === doc.filename}
                        className="text-red-500 hover:text-red-700 text-sm disabled:opacity-50"
                    >
                        {deleting === doc.filename ? '...' : '删除'}
                    </button>
                </li>
            ))}
        </ul>
    );
}
