"""
Embedding 客户端管理器

负责按配置初始化 Embedding 服务客户端，并为字段、指标和用户问题的向量化
提供统一访问入口
"""

import asyncio
from typing import List, Optional

import aiohttp
from langchain_core.embeddings import Embeddings

from app.conf.app_config import EmbeddingConfig, app_config


class TEIEmbeddings(Embeddings):
    """自定义 TEI (Text Embeddings Inference) 服务客户端"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None

    async def close(self):
        """关闭 aiohttp 客户端会话"""
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文档"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        async with self.session.post(
            f"{self.base_url}/embed",
            json={"inputs": texts, "parameters": {"normalize": True}},
        ) as response:
            result = await response.json()
            # TEI 服务返回列表格式，直接返回
            if isinstance(result, list):
                return result
            # 兼容字典格式（旧版本 TEI）
            return result.get("embeddings", result)

    async def aembed_query(self, text: str) -> List[float]:
        """向量化单个查询"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        async with self.session.post(
            f"{self.base_url}/embed",
            json={"inputs": [text], "parameters": {"normalize": True}},
        ) as response:
            result = await response.json()
            # TEI 服务返回列表格式，取第一个元素
            if isinstance(result, list):
                return result[0]
            # 兼容字典格式（旧版本 TEI）
            return result.get("embeddings", [result])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文档（同步方法）"""
        return asyncio.run(self.aembed_documents(texts))

    def embed_query(self, text: str) -> List[float]:
        """向量化单个查询（同步方法）"""
        return asyncio.run(self.aembed_query(text))


class EmbeddingClientManager:
    """管理 Embedding 服务客户端的初始化与复用"""

    def __init__(self, config: EmbeddingConfig):
        self.client: Optional[TEIEmbeddings] = None
        self.config = config

    def _get_url(self) -> str:
        """拼接 Embedding 服务地址"""
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        """显式初始化客户端，避免模块导入时立即建立外部连接"""
        self.client = TEIEmbeddings(base_url=self._get_url())

    async def close(self):
        """关闭 Embedding 客户端连接"""
        if self.client is not None:
            await self.client.close()


# 模块级单例，供整个项目复用同一套 Embedding 客户端管理器
embedding_client_manager = EmbeddingClientManager(app_config.embedding)


if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client

    async def test():
        """执行一次最小化向量化调用，验证服务是否可用"""
        text = "What is deep learning?"
        query_result = await client.aembed_query(text)
        print(query_result[:3])

    asyncio.run(test())
