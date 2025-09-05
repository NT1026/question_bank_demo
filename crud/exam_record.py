from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from crud.question import QuestionCrudManager
from database.mysql import crud_class_decorator
from models.exam_record import ExamRecord as ExamRecordModel
from schemas import exam_record as ExamRecordSchema

QuestionCrud = QuestionCrudManager()


@crud_class_decorator
class ExamRecordCrudManager:
    async def create(
        self,
        user_id: str,
        newExamRecord: ExamRecordSchema.ExamRecordCreate,
        db_session: AsyncSession,
    ):
        # Calculate score
        score = 0
        for item in newExamRecord.user_answers:
            question = await QuestionCrud.get(item.question_id)
            if question and question.answer == item.user_answer:
                score += 1

        # Create new exam record
        exam_record = ExamRecordModel(
            user_id=user_id,
            subject=newExamRecord.subject,
            score=score,
            user_answers=newExamRecord.user_answers,
        )
        db_session.add(exam_record)
        await db_session.commit()

        return exam_record

    async def get(
        self,
        exam_record_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(ExamRecordModel).where(ExamRecordModel.id == exam_record_id)
        result = await db_session.execute(stmt)
        exam_record = result.scalar_one_or_none()

        return exam_record

    async def get_by_user_id(
        self,
        user_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(ExamRecordModel).where(ExamRecordModel.user_id == user_id)
        result = await db_session.execute(stmt)
        exam_records = result.scalars().all()

        return exam_records

    async def delete(
        self,
        exam_record_id: str,
        db_session: AsyncSession,
    ):
        stmt = delete(ExamRecordModel).where(ExamRecordModel.id == exam_record_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return
