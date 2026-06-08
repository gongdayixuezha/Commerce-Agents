"use client";
import ReactMarkdown from "react-markdown";

function extractProductIds(text: string): string[] {
  const matches = text.match(/prod_\d{4}/g);
  return matches ? [...new Set(matches)] : [];
}

function extractPaymentUrl(text: string): string | null {
  const match = text.match(/https?:\/\/checkout\.stripe\.com\/\S+/);
  return match ? match[0] : null;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function MessageBubble({
  message,
  onCompare,
}: {
  message: Message;
  onCompare?: (ids: string[]) => void;
}) {
  const isUser = message.role === "user";
  const productIds = extractProductIds(message.content);
  const paymentUrl = extractPaymentUrl(message.content);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[85%] p-4 rounded-2xl ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : "bg-white shadow border rounded-bl-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none text-gray-800">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* 对比按钮 */}
        {!isUser && productIds.length >= 2 && onCompare && (
          <button
            onClick={() => onCompare(productIds.slice(0, 4))}
            className="mt-2 text-blue-600 text-sm underline hover:text-blue-800"
          >
            对比前 {Math.min(productIds.length, 4)} 个商品
          </button>
        )}

        {/* 支付链接按钮 */}
        {!isUser && paymentUrl && (
          <a
            href={paymentUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 inline-block bg-green-600 hover:bg-green-700 text-white font-medium px-5 py-2 rounded-lg text-sm transition"
          >
            去支付 💳
          </a>
        )}
      </div>
    </div>
  );
}
