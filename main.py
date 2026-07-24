"""
FastAPI 应用入口

负责创建后端应用实例，注册应用生命周期函数，并把各业务模块中的 router
挂载到同一个 app 上。HTTP 请求会先进入这里创建的 app，再按路由分发到
具体的接口处理函数。
"""

import uuid

from fastapi import FastAPI, Request

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var

# lifespan 交给 FastAPI 管理，用于在服务启动和关闭时统一初始化与释放外部客户端
app = FastAPI(
    lifespan=lifespan,
    title="E-commerce Data Query API",
    description="""
电商数据问数智能体 API

基于 LangGraph + LLM 的自然语言转 SQL 问数系统，支持：
- 自然语言问题理解与解析
- 元数据知识库语义召回
- SQL 自动生成与校验
- 数据查询与结果返回

## 核心功能

### 问数查询
- POST /api/query - 接收自然语言问题，流式返回 SQL 查询结果

## 技术栈
- FastAPI - HTTP 框架
- LangGraph - 工作流编排
- MySQL - 元数据和数仓存储
- Qdrant - 向量检索
- Elasticsearch - 全文检索
- Embedding - 文本向量化
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 把查询路由注册进应用；没有挂载时，/docs 和真实 HTTP 请求都访问不到该接口
app.include_router(query_router)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 请求被处理之前
    request_id = uuid.uuid4()
    request_id_ctx_var.set(request_id)
    response = await call_next(request)
    # 请求被处理之后
    return response
