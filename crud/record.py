import uuid
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.mysql import crud_class_decorator
from models.record import Record as RecordModel
from schemas import record as RecordSchema


@crud_class_decorator
class RecordCrudManager:
    async def create(
        self,
        user_id: str,
        newRecord: RecordSchema.RecordCreate,
        db_session: AsyncSession,
    ):
        # Compute the score
        score = 0
        for question in newRecord.user_answers:
            if question.user_answer == question.answer:
                score += 1

        # Create new exam record
        record = RecordModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            subject=newRecord.subject,
            score=score,
            user_answers=newRecord.user_answers,
            created_at=datetime.now(),
        )
        db_session.add(record)
        await db_session.commit()

        return record

    async def get(
        self,
        record_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(RecordModel).where(RecordModel.id == record_id)
        result = await db_session.execute(stmt)
        record = result.scalar_one_or_none()

        return record

    async def get_all(
        self,
        db_session: AsyncSession,
    ):
        stmt = select(RecordModel)
        result = await db_session.execute(stmt)
        records = result.scalars().all()

        return records

    async def get_by_user_id(
        self,
        user_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(RecordModel).where(RecordModel.user_id == user_id)
        result = await db_session.execute(stmt)
        records = result.scalars().all()

        return records

    async def delete(
        self,
        record_id: str,
        db_session: AsyncSession,
    ):
        stmt = delete(RecordModel).where(RecordModel.id == record_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return
