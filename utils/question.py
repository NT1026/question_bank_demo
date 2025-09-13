def sorted_answer(answer: str):
    return "".join(sorted(list(item for item in answer.upper())))


def is_invalid_answer_format(answer: str):
    return (
        not sorted_answer(answer)
        or not all(c in "ABCD" for c in sorted_answer(answer))
        or len(answer) > 4
    )
