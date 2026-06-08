"""LangChain Agent 编排"""
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL
from agent.tools import ALL_TOOLS
from observability.langfuse_trace import get_langfuse_handler

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
- 用户没有明确表示要购买时，不要主动创建支付链接
- 如果搜索结果不理想，主动建议调整搜索条件"""

llm = ChatOpenAI(
    model=LLM_MODEL,
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    temperature=0.3,
    max_tokens=2048,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=ALL_TOOLS,
    verbose=False,
    handle_parsing_errors=True,
    max_iterations=5,
)


async def chat(message: str, chat_history: list = None) -> str:
    """执行 Agent 对话"""
    langfuse_handler = get_langfuse_handler()
    config = {}
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    try:
        result = await agent_executor.ainvoke(
            {
                "input": message,
                "chat_history": chat_history or [],
            },
            config=config,
        )
        return result["output"]
    except Exception as e:
        error_msg = str(e)
        print(f"Agent error: {error_msg}")
        return f"抱歉，处理您的请求时遇到了问题：{error_msg}。请稍后重试。"

