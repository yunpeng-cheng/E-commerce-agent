# 电商数据问数智能体

基于 LangGraph 工作流的自然语言转 SQL 智能体，支持语义检索、SQL 自动生成校验与执行。

## 📄 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [运行项目](#运行项目)
- [API 接口](#api-接口)
- [Agent 工作流](#agent-工作流)
- [贡献指南](#贡献指南)

## ✨ 功能特性

- 🔍 **混合检索**：支持关键词抽取、字段召回、指标召回、取值召回
- 📊 **SQL 闭环**：自动生成 SQL、校验语法、自动修正错误 SQL
- 💬 **自然语言问答**：用户可直接用自然语言提问，系统自动生成查询
- ⚡ **流式响应**：使用 SSE（Server-Sent Events）实时展示执行进度
- 🎯 **垂直时间线**：直观展示 Agent 执行流程
- 📱 **现代化前端**：基于 Vue 3 的对话式界面

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >= 3.14 | 语言 |
| FastAPI | >= 0.139.0 | Web 框架 |
| LangGraph | >= 1.2.9 | Agent 工作流 |
| LangChain | >= 1.3.12 | LLM 集成 |
| MySQL | 8.x | 数据仓库/元数据存储 |
| Qdrant | 1.x | 向量数据库 |
| Elasticsearch | 8.x | 全文检索 |
| TEI | - | 文本嵌入服务 |
| Tenacity | >= 8.2.3 | 重试机制 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | >= 3.5.13 | 前端框架 |
| TypeScript | ~5.8.3 | 类型安全 |
| Vite | >= 6.3.5 | 构建工具 |
| Element Plus | >= 2.14.3 | UI 组件库 |
| @microsoft/fetch-event-source | >= 2.0.1 | SSE 客户端 |

## 📁 项目结构

```
├── app/                     # 后端应用代码
│   ├── agent/               # LangGraph Agent 模块
│   │   ├── nodes/           # 工作流节点
│   │   ├── graph.py         # 工作流定义
│   │   ├── state.py         # 状态定义
│   │   └── llm.py           # LLM 客户端
│   ├── api/                 # API 接口层
│   │   ├── routers/         # 路由定义
│   │   └── schemas/         # 请求/响应模型
│   ├── clients/             # 外部服务客户端
│   ├── conf/                # 配置管理
│   ├── core/                # 核心工具（日志、重试）
│   ├── entities/            # 业务实体
│   ├── models/              # 数据库模型
│   ├── prompt/              # Prompt 模板管理
│   ├── repositories/        # 数据访问层
│   ├── services/            # 业务服务层
│   └── scripts/             # 脚本工具
├── conf/                    # 配置文件
│   ├── app_config.yaml      # 应用配置
│   └── meta_config.yaml     # 元数据配置
├── docker/                  # Docker 配置
│   ├── docker-compose.yaml  # 容器编排
│   ├── mysql/               # MySQL 初始化脚本
│   └── elasticsearch/       # ES 配置
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── hooks/           # 组合式函数
│   │   ├── api/             # API 封装
│   │   └── types/           # 类型定义
│   └── vite.config.ts       # Vite 配置
├── prompts/                 # Prompt 模板文件
├── main.py                  # 后端入口
└── pyproject.toml           # Python 依赖配置
```

## 🚀 快速开始

### 环境要求

- Python >= 3.14
- Node.js >= 20
- Docker >= 24

### 安装依赖

```bash
# 后端依赖（使用 uv）
uv pip install -e .

# 前端依赖
cd frontend
npm install
```

## ⚙️ 环境配置

### 1. 启动基础设施服务

```bash
# 启动 MySQL、Qdrant、Elasticsearch
cd docker
docker-compose up -d
```

### 2. 配置文件

复制并修改配置文件：

```bash
# 后端配置
cp conf/app_config.yaml.example conf/app_config.yaml
cp conf/meta_config.yaml.example conf/meta_config.yaml
```

配置项说明：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| mysql.host | MySQL 主机 | localhost |
| mysql.port | MySQL 端口 | 3306 |
| qdrant.host | Qdrant 主机 | localhost |
| qdrant.port | Qdrant 端口 | 6333 |
| embedding.url | TEI 服务地址 | http://localhost:8080 |
| llm.model | LLM 模型名称 | deepseek-chat |

### 3. 构建元数据索引

```bash
python -m app.scripts.build_meta_knowledge --config conf/meta_config.yaml
```

## ▶️ 运行项目

### 后端服务

```bash
# 开发模式
uv run python -m uvicorn main:app --reload

# 生产模式
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看 API 文档。

### 前端服务

```bash
cd frontend
npm run dev
```

访问 `http://localhost:5173` 查看前端页面。

## 🔌 API 接口

### 查询接口

**POST** `/api/query`

请求体：
```json
{
  "query": "统计 2025 年第一季度各大区的 GMV，并按 GMV 从高到低排序"
}
```

响应：SSE 流式响应

消息类型：
- `progress` - 执行进度
- `result` - 查询结果
- `error` - 错误信息

## 🗺️ Agent 工作流

Agent 执行流程包含以下节点：

1. **抽取关键词** - 从用户问题中提取关键信息
2. **召回字段信息** - 从向量库召回相关字段
3. **召回指标信息** - 从向量库召回相关指标
4. **召回字段取值** - 从 ES 召回字段取值
5. **合并召回信息** - 合并所有召回结果
6. **过滤指标信息** - 过滤无关指标
7. **过滤表信息** - 过滤无关表
8. **增加额外上下文** - 补充 SQL 上下文
9. **生成 SQL** - LLM 生成 SQL
10. **校验 SQL** - 校验 SQL 语法
11. **校正 SQL** - 如有错误则校正
12. **执行 SQL** - 在数据仓库执行查询

## 📝 示例问题

- 统计 2025 年第一季度各大区的 GMV，并按 GMV 从高到低排序
- 统计 2025 年 3 月各商品品类的销量和销售额
- 查询华东地区 2025 年第一季度销售额最高的前 5 个商品
- 按会员等级统计 2025 年第一季度的订单数和销售额

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 工作流框架
- [FastAPI](https://github.com/tiangolo/fastapi) - 高性能 Web 框架
- [Qdrant](https://github.com/qdrant/qdrant) - 向量数据库
- [Element Plus](https://github.com/element-plus/element-plus) - Vue 3 UI 组件库
