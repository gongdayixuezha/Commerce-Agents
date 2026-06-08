"use client";

interface Product {
  id: string;
  name: string;
  price: number;
  brand: string;
  category: string;
  subcategory: string;
  rating: number;
  sales_count: number;
  stock: number;
  description: string;
}

export default function CompareModal({
  ids,
  onClose,
}: {
  ids: string[];
  onClose: () => void;
}) {
  // For now, use parsed data from chat. Better approach: fetch from API.
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[80vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">商品对比</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>
        <p className="text-sm text-gray-500 mb-4">
          对比商品: {ids.join(", ")}
        </p>
        <div className="text-center text-gray-400 py-8">
          对比功能已就绪 — 输入"对比第1个和第3个"来查看对比表格
        </div>
        <div className="flex justify-end mt-4">
          <button
            onClick={onClose}
            className="bg-gray-200 hover:bg-gray-300 px-6 py-2 rounded-lg text-sm"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}
