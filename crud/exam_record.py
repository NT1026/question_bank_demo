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

    async def get_render(
        self,
        exam_record: ExamRecordModel,
        db_session: AsyncSession,
    ):
        rendered_user_answers = []
        for item in exam_record.user_answers:
            question = await QuestionCrud.get(item["question_id"])
            if question:
                rendered_user_answers.append(
                    {
                        "question_id": item["question_id"],
                        "image_path": question.image_path,
                        "answer": question.answer,
                        "user_answer": item["user_answer"],
                        "is_correct": question.answer == item["user_answer"],
                    }
                )
        render_result = {
            "id": exam_record.id,
            "user_id": exam_record.user_id,
            "subject": exam_record.subject,
            "score": exam_record.score,
            "user_answers": rendered_user_answers,
            "created_at": exam_record.created_at,
        }

        return render_result

    async def get(
        self,
        exam_record_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(ExamRecordModel).where(ExamRecordModel.id == exam_record_id)
        result = await db_session.execute(stmt)
        exam_record = result.scalar_one_or_none()

        return exam_record

    async def get_all(
        self,
        db_session: AsyncSession,
    ):
        stmt = select(ExamRecordModel)
        result = await db_session.execute(stmt)
        exam_records = result.scalars().all()

        return exam_records

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
