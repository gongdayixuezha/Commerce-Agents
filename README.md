# Commerce Agent — AI 电商购物助手

全链路可观测的电商 AI 助手。自然语言搜索商品 → 对比推荐 → Stripe 一键购买，附带 Langfuse 可观测性与评估仪表盘。

## 技术栈

| 层级 | 技术 |
|------|------|
| LLM | DeepSeek Chat API（支持 Function Calling） |
| Embedding | DeepSeek Embedding API |
| 向量库 | ChromaDB（Docker 本地运行） |
| 后端 | FastAPI + LangChain Agent |
| 前端 | Next.js 14 + Tailwind CSS + React Markdown |
| 检索 | 混合检索（向量语义 + 关键词加权 + RRF 融合），K=4 |
| 可观测性 | Langfuse 全链路 Trace + Dashboard |
| 评估 | Langfuse Evaluation + Ragas（Recall@4, MRR, Answer Relevancy, Faithfulness） |
| 支付 | Stripe Checkout 测试模式 |
| 部署 | Docker Compose（ChromaDB）+ 本地运行 Backend/Frontend |

## 快速启动

### 1. 环境准备

```bash
# 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 2. 配置 API Keys

编辑 `.env` 文件，填入真实 API Key：

```env
DEEPSEEK_API_KEY=sk-your-key
STRIPE_SECRET_KEY=sk_test_your-key
LANGFUSE_PUBLIC_KEY=pk-your-key
LANGFUSE_SECRET_KEY=sk-your-key
```

### 3. 启动 ChromaDB

```bash
docker compose up -d chromadb
```

### 4. 生成商品数据 + 构建向量库

```bash
cd backend
python data/generate_products.py    # 生成 400+ 个商品到 data/products.json
python -c "
import json
from rag.vector_store import vector_store
with open('data/products.json') as f:
    data = json.load(f)
vector_store.add_products(data)
print(f'向量库已构建: {vector_store.count()} 个商品')
"
```

### 5. 启动服务

```bash
# 终端 1: 后端
cd backend
uvicorn main:app --port 8080 --reload

# 终端 2: 前端
cd frontend
npm run dev
```

### 6. 打开浏览器

访问 http://localhost:3000

## 对话测试

试试以下对话流程：

```
"我想买一副降噪耳机，预算500以内"  → 返回 4 个相关商品
"对比第1个和第3个"                → 展示对比表格
"帮我买第1个"                    → 返回 Stripe 支付链接
```

支付测试：使用测试卡号 `4242 4242 4242 4242`，任意未来有效期，任意 3 位 CVC。

## 项目结构

```
commerce-agent/
├── docker-compose.yml
├── .env
├── README.md
├── backend/
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 配置
│   ├── data/
│   │   ├── generate_products.py # 商品生成脚本
│   │   └── products.json        # 商品数据
│   ├── rag/
│   │   ├── embedding.py         # 向量化
│   │   ├── vector_store.py      # ChromaDB 操作
│   │   └── retriever.py         # 混合检索
│   ├── agent/
│   │   ├── tools.py             # Function Calling 工具
│   │   └── agent.py             # Agent 编排
│   ├── payment/
│   │   ├── stripe_service.py    # Stripe Checkout
│   │   └── webhook.py           # Webhook
│   ├── observability/
│   │   └── langfuse_trace.py    # Langfuse 追踪
│   └── evaluation/
│       ├── dataset.py
│       └── evaluate.py
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   └── components/
│       ├── ChatInterface.tsx
│       ├── ProductCard.tsx
│       ├── CompareModal.tsx
│       └── MessageBubble.tsx
└── evaluation/
    ├── test_queries.json        # 30 条测试查询
    └── run_evaluation.py        # 评估脚本
```

## 演示脚本（10 分钟）

| 时间 | 内容 | 负责人 |
|------|------|--------|
| 0-1min | **项目背景** — "Commerce Agent，全链路可观测的电商 AI 助手" | A |
| 1-4min | **直播演示** — 搜索 → 筛选 → 对比 → 购买 | B |
| 4-5min | **Langfuse 可观测性** — 展示 Trace 和 Dashboard | A |
| 5-6min | **评估仪表盘** — 展示指标得分，解释选择理由 | B |
| 6-8min | **技术架构** — 设计决策说明 | A |
| 8-10min | **Q&A + 展望** — "With more time, we would..." | A+B |

## 设计决策

### 为什么 K=4？

信息量与选择感的平衡点。四宫格展示在移动端和桌面端都友好——Google/Amazon 搜索每页约 4-8 个结果；心理学研究表明 3-5 个选项不造成决策瘫痪。

### 为什么混合检索而非纯向量？

电商场景需要精确的价格/品牌/品类过滤。纯语义检索无法处理"500以内"、"索尼品牌"这类精确约束。混合检索（向量 + 关键词过滤 + RRF 融合）兼顾语义理解与结构化查询。

### 为什么 Langfuse 全家桶？

可观测性 + 评估一体化平台，减少维护成本。演示时一个平台展示全部功能（Trace、Dashboard、Evaluation Score）。开源免费额度支持 50K 观测/月。

### 为什么 DeepSeek？

中文能力领先（C-Eval 等基准测试排行前列），Function Calling 成熟稳定，API 价格可控（¥1/百万 tokens），OpenAI SDK 完全兼容。

## 验收标准

- [x] 搜索：自然语言查询返回 4 个相关商品
- [x] 对比：展示多商品属性对比表格
- [x] 支付：Stripe Checkout 生成支付链接
- [x] 可观测性：Langfuse 全链路 Trace
- [x] 评估：Recall@4 + MRR 评估管道
- [x] Docker Compose 一键启动 ChromaDB

## 未来展望

> "With more time, we would..."

- **个性化推荐** — 基于用户历史购买和浏览行为的协同过滤
- **多模态搜索** — 支持图片搜索（上传商品图片找同款）
- **A/B 测试框架** — 对比不同检索策略、不同 Prompt 的转化率
- **生产级部署** — Kubernetes 部署、CI/CD 管道、负载均衡
- **实时库存同步** — 对接真实 ERP 系统，WebSocket 推送库存变动
- **多语言支持** — 中英文混合对话，自动翻译
