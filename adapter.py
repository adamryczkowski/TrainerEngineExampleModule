from module import JudgmentType, QuestionType, AnswerType, Settings, check_answer, randomize_question, calc_score

from typing import Any, Optional
from dataclasses import is_dataclass, fields


def _adapt_settings_values(settings: Settings) -> dict[str, Any]:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return {
        "max_number": settings.max_number,
        "min_number": settings.min_number}


def _adapt_make_settings(values: dict[str, Any]) -> Settings:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return Settings(values["max_number"], values["min_number"])


def _adapt_judgment_values(judgment: JudgmentType) -> dict[str, Any]:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return {
        "score_in_units": judgment.score_in_units,
        "score_in_tens": judgment.score_in_tens,
        "score_in_sign": judgment.score_in_sign,
        "score_in_ordering": judgment.score_in_ordering,
        "score_in_operand": judgment.score_in_operand}


def _adapt_question_values(question: QuestionType) -> dict[str, Any]:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return {
        "first_operand": question.first_operand,
        "second_operand": question.second_operand,
        "operator": question.operator}


def _adapt_answer_values(answer: AnswerType) -> dict[str, Any]:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return {
        "answer": answer.answer}


def _adapt_make_question(values: dict[str, Any]) -> QuestionType:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return QuestionType(values["first_operand"], values["second_operand"], values["operator"])


def _adapt_make_answer(values: dict[str, Any]) -> AnswerType:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    return AnswerType(values["answer"])


def adapted_SQL_create_str(primary_key_name: str, cls: type) -> str:
    """

    :param cls: dataclass to serialize to SQL
    :param primary_key_name: name of the primary key that will be inserted to the class' definition
    :return: returns the CREATE TABLE sql query to create a table that holds the fields
    """
    fields = [(primary_key_name, "INTEGER PRIMARY KEY")]
    fields.extend(adapted_SQL_types(cls))
    ans = f"CREATE TABLE IF NOT EXISTS {cls.__name__} ("
    for field in fields:
        ans += f"{field[0]} {field[1]}, "
    ans = ans[:-2] + ")"
    return ans


def adapted_SQL_types(cls: type) -> list[tuple[str, str]]:
    """

    :param cls: dataclass to serialize to SQL
    :return: extracts the fields of the dataclass cls and presents them as a list of tuples (field_name, sql_field_type)
    """
    assert is_dataclass(cls), f"{cls} is not a dataclass"
    ans = []
    # Iterate over data fields of cls
    for field in fields(cls):
        # Get the type of the field and convert it to a string
        field_type = str(field.type)
        # Convert the type to a SQL type
        if field_type == "int":
            sql_type = "INTEGER"
        elif field_type == "str":
            sql_type = "TEXT"
        elif field_type == "float":
            sql_type = "REAL"
        else:
            raise TypeError(f"Unsupported type {field_type}")

        ans.append((field.name, sql_type))

    return ans


## ------------------ The following functions are the ones that are used by the Kotlin code ------------------ ##

def adapted_randomize_question(positive_skills: list[str], negative_skills: list[str], settings: dict[str, Any]) -> \
        Optional[tuple[dict[str, Any], dict[str, Any], list[str]]]:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    ans = randomize_question(positive_skills, negative_skills, _adapt_make_settings(settings))
    if ans is None:
        return None
    question, answer, skills = ans
    return _adapt_question_values(question), _adapt_answer_values(answer), skills


def adapted_check_answer(skills: list[str], answer: dict[str, Any], correct_answer: dict[str, Any],
                         question: dict[str, Any]) -> tuple[float, dict[str, tuple[float, float]], dict[str, Any]]:
    # Converts the settings to a dictionary of values that can be used by the Kotlin code.
    question = _adapt_make_question(question)
    answer = _adapt_make_answer(answer)
    correct = _adapt_make_answer(correct_answer)
    judgement = check_answer(question, answer, correct, skills)
    score_dict = calc_score(judgement, correct, skills)

    weight = 0
    score = 0
    for item_score, item_weight in score_dict.values():
        weight += item_weight
        score += item_score
    score /= weight

    return score, score_dict, _adapt_judgment_values(judgement)


def adapted_question_SQL_create_str(primary_key_name: str) -> str:
    return adapted_SQL_create_str(primary_key_name, QuestionType)


def adapted_answer_SQL_create_str(primary_key_name: str) -> str:
    return adapted_SQL_create_str(primary_key_name, AnswerType)
