from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.mysql import crud_class_decorator
from models.question import Question as QuestionModel
from schemas import question as QuestionSchema


@crud_class_decorator
class QuestionCrudManager:
    async def create(
        self,
        newQuestion: QuestionSchema.QuestionCreate,
        db_session: AsyncSession,
    ):
        # Check if question already exists
        stmt = select(QuestionModel).where(
            QuestionModel.image_path == newQuestion.image_path,
        )
        result = await db_session.execute(stmt)
        exist = result.scalar_one_or_none()
        if exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Question already exists",
            )

        # Create new question
        question = QuestionModel(
            subject=newQuestion.subject,
            image_path=newQuestion.image_path,
            answer=newQuestion.answer,
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

    async def delete(
        self,
        question_id: str,
        db_session: AsyncSession,
    ):
        stmt = delete(QuestionModel).where(QuestionModel.id == question_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return
