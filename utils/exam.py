from random import sample

from auth.image import generate_image_token
from crud.exam_record import ExamRecordCrudManager
from crud.question import QuestionCrudManager
from settings.subject import SUBJECT_EXAM_INFO

ExamRecordCrud = ExamRecordCrudManager()
QuestionCrud = QuestionCrudManager()


async def exam_dashboard_data(ids):
    records = []
    all_correct = 0
    all_questions = 0

    for exam_id in ids:
        exam = await ExamRecordCrud.get(exam_id)
        records.append(
            {
                "exam_record_id": exam_id,
                "score": exam.score,
                "question_count": len(exam.user_answers),
                "accuracy": (
                    f"{(exam.score / len(exam.user_answers)) * 100:.2f}%"
                    if len(exam.user_answers)
                    else "0.00%"
                ),
                "created_at": exam.created_at,
            }
        )
        all_correct += exam.score
        all_questions += len(exam.user_answers)

    records.sort(key=lambda x: x["created_at"], reverse=True)
    all_accuracy = (
        f"{(all_correct / all_questions) * 100:.2f}%" if all_questions else "0.00%"
    )

    return {
        "all_correct": all_correct,
        "all_questions": all_questions,
        "all_accuracy": all_accuracy,
        "exam_records": records,
    }


async def get_exam_render_info(user_id):
    exam_records = await ExamRecordCrud.get_by_user_id(user_id)
    exam_lists = {
        exam_type: await exam_dashboard_data(
            [item.id for item in exam_records if item.exam_type == exam_type]
        )
        for exam_type in SUBJECT_EXAM_INFO
    }
    return exam_lists


async def random_choose_questions(exam_type, current_user_id):
    subject = SUBJECT_EXAM_INFO[exam_type]["subject"]
    questions = await QuestionCrud.get_by_subject(subject)

    question_num = SUBJECT_EXAM_INFO[exam_type]["question_count"]
    selected_quesions = sample(questions, min(question_num, len(questions)))

    # Generate image token for each question
    for question in selected_quesions:
        question.token = generate_image_token(str(current_user_id), question.id)

    return selected_quesions
