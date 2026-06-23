'use client';

import { useRef, useState } from 'react';
import toast from 'react-hot-toast';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || '';

export default function UploadArea({ onUploadSuccess }: { onUploadSuccess: () => void }) {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleUpload = async (files: FileList | null) => {
        if (!files || files.length === 0) return;
        const file = files[0];
        // 验证类型和大小
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (!['pdf', 'txt', 'md'].includes(ext || '')) {
            toast.error('仅支持 PDF、TXT、Markdown 文件');
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            toast.error('文件大小超过 10MB');
            return;
        }

        setUploading(true);
        setProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', `${API_BASE}/upload`);
            xhr.upload.onprogress = (e) => {
                if (e.total) {
                    setProgress(Math.round((e.loaded / e.total) * 100));
                }
            };
            xhr.onload = () => {
                if (xhr.status === 200) {
                    toast.success('上传成功！');
                    onUploadSuccess();
                } else {
                    toast.error('上传失败：' + xhr.statusText);
                }
                setUploading(false);
                setProgress(0);
                if (fileInputRef.current) fileInputRef.current.value = '';
            };
            xhr.onerror = () => {
                toast.error('网络错误');
                setUploading(false);
                setProgress(0);
            };
            xhr.send(formData);
        } catch (err) {
            toast.error('上传失败');
            setUploading(false);
            setProgress(0);
        }
    };

    return (
        <div className="mb-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition">
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.txt,.md"
                    onChange={(e) => handleUpload(e.target.files)}
                    disabled={uploading}
                    className="hidden"
                    id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer block">
                    <span className="text-gray-600">拖拽或点击上传文件</span>
                    <span className="text-xs text-gray-400 block mt-1">支持 PDF、TXT、Markdown（≤10MB）</span>
                </label>
            </div>
            {uploading && (
                <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                    </div>
                    <span className="text-xs text-gray-500">{progress}%</span>
                </div>
            )}
        </div>
    );
}
