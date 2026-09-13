# 大学生软件实训教学 AI 检查评价系统

基于大模型的软件实训成果自动化检查、评价与管理平台，面向教师与学生，提供
成果上传解析、智能核查、多维度评价、报表导出等核心能力。

## 技术栈

| 层次 | 选型 |
| ---- | ---- |
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy 2.0（异步）/ SQLite（可切换 PostgreSQL）|
| 前端 | React 18 + Vite + TypeScript + Ant Design 5 + ECharts |
| 大模型 | 抽象 Provider 层，同时支持本地（Ollama）与云端（OpenAI 兼容）|
| 文件解析 | python-docx / PyMuPDF / PaddleOCR（可选）|
| 报表 | openpyxl（Excel）/ reportlab（PDF）/ matplotlib（图表）|

## 目录结构

```
Aiyana/
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── api/        # 路由层（auth/users/tasks/submissions/...）
│   │   ├── core/       # 配置、安全
│   │   ├── db/         # 数据库会话、初始化
│   │   ├── models/     # SQLAlchemy 模型
│   │   ├── schemas/    # Pydantic 模型
│   │   └── services/   # 业务服务（llm/parsing/inspection/evaluation/report）
│   ├── requirements.txt
│   └── .env.example
├── frontend/           # React 前端
│   └── src/{api,pages,components,layouts,store,router,types}
├── docs/开发文档.md     # 详细开发文档
└── question.txt        # 原始需求
```

## 快速开始

### 1. 启动大模型（本地 Ollama，可选）

```bash
# 安装 Ollama 后拉取模型
ollama pull qwen2.5:7b
ollama serve
```

> 也可跳过本地模型，改用云端 API（见 `.env` 中 `LLM_PROVIDER=openai`）。

### 2. 启动后端

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env      # 按需修改 LLM_PROVIDER / API Key
python -m uvicorn app.main:app --reload --port 8000
```

- 接口文档：http://localhost:8000/docs
- 默认账号：`teacher/teacher123`、`student/student123`

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev               # http://localhost:5173
```

访问 http://localhost:5173 登录后即可使用。

## 核心流程

1. **教师** 发布实训任务，填写验收要求，配置评价指标与权重。
2. **学生** 上传成果（Word / PDF / 截图 / 代码），系统自动解析并结构化抽取。
3. **AI 核查** 比对任务要求与成果，识别偏离项、逻辑漏洞、缺失步骤。
4. **AI 评价** 按指标客观评分，**教师** 可手动调整并补充评语。
5. **报表导出** 生成学生单份报告或班级统计（Excel / PDF，含雷达图/柱状图）。

详细说明见 [docs/开发文档.md](docs/开发文档.md)。
