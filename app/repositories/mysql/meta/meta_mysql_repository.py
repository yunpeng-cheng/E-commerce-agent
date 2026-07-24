"""
元数据库 MySQL 仓储
"""

from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.retry import async_mysql_retry
from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.column_metric import ColumnMetricMySQL
from app.models.metric_info import MetricInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.column_metric_mapper import ColumnMetricMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import TableInfoMapper


class MetaMySQLRepository:
    """负责把元数据业务实体持久化到 Meta MySQL"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @async_mysql_retry
    async def save_table_infos(self, table_infos: list[TableInfo]):
        """批量保存表元数据。使用 ON DUPLICATE KEY UPDATE 保证幂等性"""
        if not table_infos:
            return

        for table_info in table_infos:
            model_instance = TableInfoMapper.to_model(table_info)
            # 创建插入语句
            stmt = insert(TableInfoMySQL).values(
                id=model_instance.id,
                name=model_instance.name,
                role=model_instance.role,
                description=model_instance.description,
            )
            # 主键冲突时更新其他字段
            update_stmt = stmt.on_duplicate_key_update(
                name=stmt.inserted.name,
                role=stmt.inserted.role,
                description=stmt.inserted.description,
            )
            await self.session.execute(update_stmt)

    @async_mysql_retry
    async def save_column_infos(self, column_infos: list[ColumnInfo]):
        """批量保存字段元数据。使用 ON DUPLICATE KEY UPDATE 保证幂等性"""
        if not column_infos:
            return

        for column_info in column_infos:
            model_instance = ColumnInfoMapper.to_model(column_info)
            stmt = insert(ColumnInfoMySQL).values(
                id=model_instance.id,
                name=model_instance.name,
                type=model_instance.type,
                role=model_instance.role,
                examples=model_instance.examples,
                description=model_instance.description,
                alias=model_instance.alias,
                table_id=model_instance.table_id,
            )
            update_stmt = stmt.on_duplicate_key_update(
                name=stmt.inserted.name,
                type=stmt.inserted.type,
                role=stmt.inserted.role,
                examples=stmt.inserted.examples,
                description=stmt.inserted.description,
                alias=stmt.inserted.alias,
                table_id=stmt.inserted.table_id,
            )
            await self.session.execute(update_stmt)

    @async_mysql_retry
    async def save_metric_infos(self, metric_infos: list[MetricInfo]):
        """批量保存指标元数据。使用 ON DUPLICATE KEY UPDATE 保证幂等性"""
        if not metric_infos:
            return

        for metric_info in metric_infos:
            model_instance = MetricInfoMapper.to_model(metric_info)
            stmt = insert(MetricInfoMySQL).values(
                id=model_instance.id,
                name=model_instance.name,
                description=model_instance.description,
                relevant_columns=model_instance.relevant_columns,
                alias=model_instance.alias,
            )
            update_stmt = stmt.on_duplicate_key_update(
                name=stmt.inserted.name,
                description=stmt.inserted.description,
                relevant_columns=stmt.inserted.relevant_columns,
                alias=stmt.inserted.alias,
            )
            await self.session.execute(update_stmt)

    @async_mysql_retry
    async def save_column_metrics(self, column_metrics: list[ColumnMetric]):
        """批量保存字段与指标的关联关系。使用 ON DUPLICATE KEY UPDATE 保证幂等性"""
        if not column_metrics:
            return

        for column_metric in column_metrics:
            model_instance = ColumnMetricMapper.to_model(column_metric)
            stmt = insert(ColumnMetricMySQL).values(
                column_id=model_instance.column_id,
                metric_id=model_instance.metric_id,
            )
            # 联合主键冲突时更新（实际上不会更新，只是避免报错）
            update_stmt = stmt.on_duplicate_key_update(
                column_id=stmt.inserted.column_id,
                metric_id=stmt.inserted.metric_id,
            )
            await self.session.execute(update_stmt)

    @async_mysql_retry
    async def get_column_info_by_id(self, id: str) -> ColumnInfo | None:
        """按字段 id 查询字段元数据，供召回信息合并阶段补齐字段上下文"""

        column_info: ColumnInfoMySQL | None = await self.session.get(
            ColumnInfoMySQL, id
        )
        if column_info:
            return ColumnInfoMapper.to_entity(column_info)
        else:
            return None

    @async_mysql_retry
    async def get_table_info_by_id(self, id: str) -> TableInfo | None:
        """按表 id 查询表元数据，最终组装成提示词里的表结构信息"""

        table_info: TableInfoMySQL | None = await self.session.get(TableInfoMySQL, id)
        if table_info:
            return TableInfoMapper.to_entity(table_info)
        else:
            return None

    @async_mysql_retry
    async def get_key_columns_by_table_id(self, table_id: str) -> list[ColumnInfo]:
        """查询指定表的主外键字段，避免 Join 关键字段被向量召回漏掉"""

        # 主外键字段用于后续生成 join 条件，不能完全依赖向量召回命中
        sql = "select * from column_info where table_id = :table_id and role in ('primary_key','foreign_key')"
        # :table_id 是 SQLAlchemy text SQL 的占位符，实际值通过第二个参数传入
        result = await self.session.execute(text(sql), {"table_id": table_id})
        # mappings() 会把结果行转成类似字典的结构，便于解包成 ColumnInfo
        return [ColumnInfo(**dict(row)) for row in result.mappings().fetchall()]