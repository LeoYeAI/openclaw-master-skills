#!/usr/bin/env python3
"""
本地化轻量级数据库封装
使用SQLite + SQLAlchemy ORM
支持基础CRUD操作，通过继承BaseDao快速实现各表的Dao层
"""
import datetime
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Select, Table, MetaData, select, or_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.expression import text

from skills.smyx_common.scripts.config import ConstantEnum, ApiEnum

from skills.smyx_common.scripts.util import StringUtil, DatetimeUtil, FileUtil

from skills.smyx_common.scripts.base import BaseMixin, BaseDao

# 基础模型类
Base = declarative_base()

# 泛型类型，用于返回对应模型实例
T = TypeVar('T', bound=Base)

meta = MetaData()

DATABASE_URL = ApiEnum.DATABASE_URL


class BaseModelMixin(BaseMixin):

    @classmethod
    def load(cls, source: dict):
        """
        获取源枚举
        :param source: 源
        :return: User
        """
        column_names = cls.__table__.columns.keys()
        user_dict = {k: source.get(StringUtil.snake_to_camel(k)) for k in column_names}
        user_dict["create_time"] = DatetimeUtil.parse(user_dict["create_time"])
        user_dict["update_time"] = DatetimeUtil.parse(user_dict["update_time"])
        model = cls(**user_dict)
        return model


class Dao(BaseDao):
    """
    基础Dao类，提供通用的CRUD操作
    子类只需配置__model__和__tablename__即可使用
    """
    __model__: Type[T] = None  # 对应的模型类，子类必须配置
    __tablename__: str = None  # 表名，子类必须配置

    def get_db_path(self, db_path):
        import os

        cwd = os.getcwd()
        workspace = os.path.dirname(cwd)
        workspace = os.path.dirname(workspace)
        workspace = os.environ.get('OPENCLAW_WORKSPACE', workspace)
        parent_dir = os.path.join(workspace, "data")
        FileUtil.mkdir(parent_dir)
        db_path = os.path.join(parent_dir, db_path)

        return db_path

    def __init__(self, db_path: str = None):
        """
        初始化Dao
        :param db_path: SQLite数据库文件路径
        """

        if not db_path:
            db_path = "smyx-common-claw.db"
            db_path = self.get_db_path(db_path)

        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # 创建会话工厂
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        # 初始化表结构
        self._create_tables()
        self._alter_tables()

    def _create_tables(self) -> None:
        """创建所有表结构"""
        Base.metadata.create_all(bind=self.engine)

    def _alter_tables(self) -> None:
        """创建所有表结构"""
        sql_statement = "ALTER TABLE sys_user ADD COLUMN source_id INT;"

        # 3. 执行语句
        try:
            with self.engine.connect() as connection:
                connection.execute(text(sql_statement))
                connection.commit()  # 对于数据定义语言(DDL)，需要显式提交
        except Exception as e:
            connection.rollback()
            if len(e.args) and "duplicate column name" in e.args[0]:
                pass
            else:
                raise

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    def save(self, model) -> T:
        """
        创建新记录
        :param kwargs: 字段键值对
        :return: 创建的模型实例
        """

        try:
            return self.add(
                model
            )

        except Exception as e:
            return self.update(
                model
            )

    def add(self, model) -> T:
        """
        创建新记录
        :param kwargs: 字段键值对
        :return: 创建的模型实例
        """
        session = self.get_session()
        try:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model
        finally:
            session.close()

    def create(self, **kwargs) -> T:
        """
        创建新记录
        :param kwargs: 字段键值对
        :return: 创建的模型实例
        """
        instance = self.__model__(**kwargs)
        return self.add(instance)

    def get_by_id(self, record_id: int) -> Optional[T]:
        """
        根据ID查询记录
        :param record_id: 记录ID
        :return: 模型实例或None
        """
        session = self.get_session()
        try:
            return session.query(self.__model__).filter(self.__model__.id == record_id).first()
        finally:
            session.close()

    def get_by_username(self, username: str) -> Optional[T]:
        """
        根据ID查询记录
        :param record_id: 记录ID
        :return: 模型实例或None
        """
        session = self.get_session()
        try:
            or_(
                self.__model__.del_flag == 0,
                self.__model__.del_flag.is_(None)  # 关键：使用 .is_(None) 来判断 SQL 的 NULL
            )
            return session.query(self.__model__).filter(self.__model__.username == username,
                                                        or_(
                                                            self.__model__.del_flag == 0,
                                                            self.__model__.del_flag.is_(None)
                                                            # 关键：使用 .is_(None) 来判断 SQL 的 NULL
                                                        )).first()
        finally:
            session.close()

    def list(self, filters: Optional[Dict[str, Any]] = None, limit: Optional[int] = None,
             offset: Optional[int] = None) -> List[T]:
        """
        查询记录列表
        :param filters: 过滤条件字典，如{"name": "张三", "age": 18}
        :param limit: 最大返回数量
        :param offset: 偏移量
        :return: 模型实例列表
        """
        session = self.get_session()
        try:
            query = session.query(self.__model__)
            # .where(self.__model__.id != 2, self.__model__.id == 1))

            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.__model__, key) == value)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        finally:
            session.close()

    def update(self, model) -> Optional[T]:
        """
        更新记录
        :param record_id: 记录ID
        :param kwargs: 要更新的字段键值对
        :return: 更新后的模型实例或None
        """
        session = self.get_session()
        try:
            instance = session.query(self.__model__).filter(self.__model__.id == model.id).first()
            if not instance:
                return None

            column_names = self.__model__.__table__.columns.keys()

            for key in column_names:
                value = getattr(model, key)
                setattr(instance, key, value)

            session.commit()
            session.refresh(instance)
            return instance
        finally:
            session.close()

    def modify(self, record_id: int, **kwargs) -> Optional[T]:
        """
        更新记录
        :param record_id: 记录ID
        :param kwargs: 要更新的字段键值对
        :return: 更新后的模型实例或None
        """
        session = self.get_session()
        try:
            instance = session.query(self.__model__).filter(self.__model__.id == record_id).first()
            if not instance:
                return None

            for key, value in kwargs.items():
                setattr(instance, key, value)

            session.commit()
            session.refresh(instance)
            return instance
        finally:
            session.close()

    def update_by_username(self, username: str, **kwargs) -> Optional[T]:
        """
        更新记录
        :param username: 记录ID
        :param kwargs: 要更新的字段键值对
        :return: 更新后的模型实例或None
        """
        session = self.get_session()
        try:
            instance = session.query(self.__model__).filter(self.__model__.username == username).first()
            if not instance:
                return None

            for key, value in kwargs.items():
                setattr(instance, key, value)

            session.commit()
            session.refresh(instance)
            return instance
        finally:
            session.close()

    def delete(self, record_id: int) -> bool:
        """
        删除记录
        :param record_id: 记录ID
        :return: 删除成功返回True，失败返回False
        """
        session = self.get_session()
        try:
            instance = session.query(self.__model__).filter(self.__model__.id == record_id).first()
            if not instance:
                return False

            session.delete(instance)
            session.commit()
            return True
        finally:
            session.close()

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数量
        :param filters: 过滤条件字典
        :return: 记录数量
        """
        session = self.get_session()
        try:
            query = session.query(func.count(self.__model__.id))

            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.__model__, key) == value)

            return query.scalar()
        finally:
            session.close()


class User(Base, BaseModelMixin):
    """用户模型"""
    __tablename__ = "sys_user"

    id = Column(String(32), primary_key=True, index=True)
    source_id = Column(String(32), comment="源头id")
    username = Column(String(100), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(45), unique=True, index=True, comment="邮箱")
    birthday = Column(DateTime, unique=True, index=True, comment="邮箱")
    sex = Column(Integer, comment="性别")
    age = Column(Integer, comment="年龄")
    token = Column(String(500), comment="token")
    open_token = Column(String(1000), comment="开放token")
    source = Column(String(50), comment="token")
    del_flag = Column(Integer, comment="是否删除", default=0)
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    SourceEnum = ConstantEnum.SourceEnum


class UserDao(Dao):
    """用户Dao，继承BaseDao即可拥有所有基础CRUD功能"""
    __model__ = User
    __tablename__ = "users"


if __name__ == "__main__":
    pass
