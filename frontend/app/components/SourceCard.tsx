export default function SourceCard({ source }: { source: any }) {
  return (
    <div className="border-l-2 border-blue-300 pl-2 my-1 text-xs bg-gray-50 rounded p-1">
      <div className="font-medium">{source.filename}</div>
      <div className="text-gray-600 truncate">{source.chunk}</div>
      <div className="text-gray-400">相似度: {source.score.toFixed(3)}</div>
    </div>
  );
}
