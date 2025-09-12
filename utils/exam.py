from crud.exam_record import ExamRecordCrudManager

ExamRecordCrud = ExamRecordCrudManager()


async def get_exam_summary(ids):
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
                "accuracy": f"{(exam.score / len(exam.user_answers)) * 100:.2f}%" if len(exam.user_answers) else "0.00%",
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
