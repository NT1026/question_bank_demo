from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.mysql import crud_class_decorator
from models.question import Question as QuestionModel


@crud_class_decorator
class QuestionCrudManager:
    async def create(
        self,
        id: str,
        subject: str,
        image_path: str,
        answer: str,
        db_session: AsyncSession,
    ):
        question = QuestionModel(
            id=id,
            subject=subject,
            image_path=image_path,
            answer=answer,
        )
        db_session.add(question)
        await db_session.commit()

        return question

    async def get(
        self,
        question_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(QuestionModel).where(QuestionModel.id == question_id)
        result = await db_session.execute(stmt)
        question = result.scalar_one_or_none()

        return question

    async def get_by_subject(
        self,
        subject: str,
        db_session: AsyncSession,
    ):
        stmt = select(QuestionModel).where(QuestionModel.subject == subject)
        result = await db_session.execute(stmt)
        questions = result.scalars().all()

        return questions
    
    async def get_by_filename(
        self,
        filename: str,
        db_session: AsyncSession,
    ):
        stmt = select(QuestionModel).where(QuestionModel.image_path.contains(filename))
        result = await db_session.execute(stmt)
        questions = result.scalars().all()

        return questions

    async def delete_by_filename(
        self,
        filename: str,
        db_session: AsyncSession,
    ):
        stmt = delete(QuestionModel).where(QuestionModel.image_path.contains(filename))
        await db_session.execute(stmt)
        await db_session.commit()

        return
