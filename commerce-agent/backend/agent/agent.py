"""LangChain Agent 编排 + Langfuse 追踪"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
from agent.tools import ALL_TOOLS
from langfuse import observe
from observability.langfuse_trace import get_langfuse

SYSTEM_PROMPT = """你是一个专业的电商购物助手 Commerce Agent，帮助用户搜索、比较和购买商品。

## 你的能力
1. **搜索商品**: 理解用户需求，搜索最相关的商品（每次展示 4 个）
2. **对比商品**: 当用户想对比商品时，展示详细的属性对比表格
3. **创建支付**: 当用户决定购买时，生成 Stripe 支付链接

## 行为规则
- 每次搜索默认展示 4 个最相关商品（K=4）
- 用户说"对比第X和第Y个"时，提取 product_id 调用 compare_products
- 用户说"买第X个"或"下单"时，提取 product_id 调用 create_payment
- 回复简洁友好，用中文
- 用户没有明确表示要购买时，不要主动创建支付链接"""

llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    temperature=0.3,
    max_tokens=2048,
)

agent = create_agent(
    model=llm,
    tools=ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
)


@observe(name="commerce-agent-chat")
async def chat(message: str, chat_history: list = None) -> str:
    """执行 Agent 对话，Langfuse 自动追踪"""
    messages = []
    if chat_history:
        for h in chat_history[-10:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=message))

    try:
        result = await agent.ainvoke({"messages": messages})
        output_messages = result.get("messages", [])

        # Extract final response
        for msg in reversed(output_messages):
            if isinstance(msg, AIMessage) and msg.content:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    continue
                return msg.content

        return "抱歉，未能生成有效回复。"

    except Exception as e:
        print(f"Agent error: {e}")
        return f"抱歉，处理您的请求时遇到了问题。请稍后重试。"
