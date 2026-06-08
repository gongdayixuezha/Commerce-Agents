"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const WELCOME_MESSAGE = `👋 你好！我是 **Commerce Agent**，你的 AI 电商购物助手。

我可以帮你：
- 🔍 **搜索商品** — 告诉我你想买什么
- 📊 **对比商品** — 说"对比第1个和第3个"
- 💳 **一键支付** — 说"买第1个"即可生成支付链接

试试说：*"我想买一副降噪耳机，预算500以内"*`;

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: WELCOME_MESSAGE },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `抱歉，服务暂时不可用：${err instanceof Error ? err.message : "未知错误"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white text-lg">
            C
          </div>
          <div>
            <h1 className="text-xl font-bold">Commerce Agent</h1>
            <p className="text-sm text-gray-500">AI 电商购物助手 · 搜索 → 对比 → 购买</p>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 chat-scroll space-y-2">
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
            onCompare={(ids) => setCompareIds(ids)}
          />
        ))}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white shadow border rounded-2xl rounded-bl-sm px-6 py-4">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
            placeholder="输入你想买的商品..."
            disabled={loading}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 text-sm"
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium px-6 py-3 rounded-xl transition text-sm"
          >
            发送
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          Commerce Agent v1.0 · DeepSeek + Stripe · 测试环境
        </p>
      </div>

      {/* Compare Modal (simplified) */}
      {compareIds.length > 0 && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setCompareIds([])}>
          <div className="bg-white rounded-2xl max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold mb-2">商品对比</h2>
            <p className="text-sm text-gray-500 mb-4">
              选中商品: {compareIds.join(", ")}
            </p>
            <p className="text-sm text-gray-600">
              在聊天中输入 <code className="bg-gray-100 px-1 rounded">对比{compareIds.join("和")}</code> 查看详细对比表格
            </p>
            <button
              onClick={() => setCompareIds([])}
              className="mt-4 bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-lg text-sm w-full"
            >
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
