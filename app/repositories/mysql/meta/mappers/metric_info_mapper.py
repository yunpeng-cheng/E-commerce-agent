"""
MetricInfo 映射器

负责指标元数据业务实体和 ORM 模型之间做转换，使指标入库过程保持
“业务实体 -> Mapper -> ORM 模型”的清晰分层
"""

from dataclasses import asdict
from app.entities.metric_info import MetricInfo
from app.models.metric_info import MetricInfoMySQL


class MetricInfoMapper:
    """负责 `MetricInfo` 与 `MetricInfoMySQL` 之间的双向转换"""

    @staticmethod
    def to_entity(model: MetricInfoMySQL) -> MetricInfo:
        """把指标 ORM 模型转换为业务实体"""
        return MetricInfo(
            id=model.id,
            name=model.name,
            description=model.description,
            relevant_columns=model.relevant_columns,
            alias=model.alias,
        )

    @staticmethod
    def to_model(entity: MetricInfo) -> MetricInfoMySQL:
        """把指标业务实体转换为 ORM 模型"""
        return MetricInfoMySQL(**asdict(entity))
