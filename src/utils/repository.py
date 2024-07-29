import os
import abc
from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, update
from src.database.db_config import async_session_maker


class AbstractRepository(ABC):
    @abc.abstractmethod
    def add_one(self, data, path=None):
        raise NotImplemented()

    @abc.abstractmethod
    def get_one(self, filters):
        raise NotImplemented()

    @abc.abstractmethod
    def delete_one(self, filters):
        raise NotImplemented()

    @abc.abstractmethod
    def update_one(self, filters, values):
        raise NotImplemented()

    @abc.abstractmethod
    def update_one_db(self, filters, values):
        raise NotImplemented()

    @abc.abstractmethod
    def get_all_by_filter(self, filters=None, order=None, limit=None):
        raise NotImplemented()


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict):
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = insert(self.model).values(data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one_or_none()

    async def delete_one(self, filters):
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = delete(self.model).where(*filters)
            await session.execute(stmt)
            await session.commit()

    async def get_one(self, filters):
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = select(self.model).filter(*filters)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def update_one(self, filters, values):
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = (
                update(self.model).filter(*filters).values(values).returning(self.model)
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def update_one_db(self, filters, values):
        pass

    async def get_all_by_filter(self, filters=None, order=None, limit=None):
        async with async_session_maker() as session:
            session: AsyncSession

            if limit:
                stmt = select(self.model).filter(*filters).order_by(order).limit(limit)
            elif not filters:
                stmt = select(self.model)
            else:
                stmt = select(self.model).filter(*filters).order_by(order)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res


class LocalFileRepository(AbstractRepository):
    async def update_one(self, filters, values):
        pass

    async def update_one_db(self, filters, values):
        pass

    async def get_all_by_filter(self, filters, order, limit=None):
        pass

    async def get_one(self, filters):
        pass

    async def add_one(self, data, path=None):
        with open(path, "wb") as file:
            file.write(data)

    async def delete_one(self, filters: str):
        os.remove(filters)


class ChromaRepository(AbstractRepository):
    collection = None
    model = None

    async def update_one(self, filters, values):
        return self.collection.query(query_texts=[filters], n_results=values)

    async def update_one_db(self, filters, values):
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = (
                update(self.model).filter(*filters).values(values).returning(self.model)
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def get_all_by_filter(self, filters=None, order=None, limit=None):
        async with async_session_maker() as session:
            session: AsyncSession

            if limit and filters and order:
                stmt = select(self.model).filter(*filters).order_by(order).limit(limit)
            elif filters and order:
                stmt = select(self.model).filter(*filters).order_by(order)
            else:
                stmt = select(self.model)
            res = await session.execute(stmt)
            res = [row[0] for row in res.all()]
            return res

    async def add_one(self, data):
        async with async_session_maker() as session:
            session: AsyncSession
            stmt = insert(self.model).values(data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            db_object = res.scalar_one_or_none()

        self.collection.add(
            documents=[db_object.title],
            ids=[str(db_object.id)],
        )

        return db_object

    async def get_one(self, filters):
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = select(self.model).filter(*filters)
            res = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def delete_one(self, filters):
        self.collection.delete(filters[1])
        del filters[1]
        async with async_session_maker() as session:
            session: AsyncSession

            stmt = delete(self.model).where(*filters)
            await session.execute(stmt)
            await session.commit()
