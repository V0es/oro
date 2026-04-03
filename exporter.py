import json
from collections import defaultdict
from typing import Iterable

from sqlalchemy import Row, select
from sqlalchemy.orm import Session

from config import get_settings
from models import Option, Question, QuestionType, Respondent, Response, Survey

settings = get_settings()


def fetch_survey_data(session: Session) -> Iterable[Row]:
    """Получение данных из базы

    Args:
        session (Session): Объект сессии

    Returns:
        Iterable[Row]: Коллекция строк БД
    """
    stmt = (
        select(
            Survey.id.label("survey_id"),
            Respondent.id.label("respondent_id"),
            Question.name.label("question_name"),
            Question.text.label("question_text"),
            Question.type.label("question_type"),
            Option.code.label("option_code"),
            Option.text.label("option_text"),
            Response.text.label("response_text"),
            Response.order.label("response_order"),
        )
        .select_from(Response)
        .join(Respondent, Respondent.id == Response.respondent_id)
        .join(Survey, Survey.id == Respondent.survey_id)
        .join(Question, Question.id == Response.question_id)
        .outerjoin(Option, Option.id == Response.option_id)
        .order_by(
            Survey.id,
            Respondent.id,
            Question.name,
            Response.order.nulls_last(),
        )
    )

    result = session.execute(stmt).all()
    return result


def convert_data_to_dict(rows: Iterable[Row]) -> dict:
    """Конвертация строк БД во вложенные словари
    survey -> respondent -> question -> option

    Args:
        rows (Iterable[Row]): Строки БД

    Returns:
        dict: Итоговый объект
    """
    result = {}

    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        grouped[row.survey_id][str(row.respondent_id)][row.question_name].append(row)

    for survey_id, respondents in grouped.items():
        survey_data = {}

        for respondent_id, questions in respondents.items():
            respondent_data = {}

            for question_name, rows in questions.items():
                first = rows[0]

                qusetion_data = {
                    "type": first.question_type.name,
                    "text": first.question_text,
                }

                if first.question_type == QuestionType.TEXT:
                    qusetion_data["answer"] = first.response_text

                elif first.question_type == QuestionType.SINGLE:
                    qusetion_data["answer"] = {
                        "code": first.option_code,
                        "text": first.option_text,
                    }

                else:
                    qusetion_data["answer"] = [
                        {
                            "code": row.option_code,
                            "text": row.option_text,
                            "order": row.response_order,
                        }
                        for row in rows
                    ]
                respondent_data[question_name] = qusetion_data
            survey_data[respondent_id] = respondent_data
        result[survey_id] = survey_data
    return result


def save_jsons(surveys: dict):
    """Сохраниение выходных данных в json файлы

    Args:
        surveys (dict): Аггрегированные объекты опросов
    """
    for survey_id, respondent_data in surveys.items():
        with open(settings.output.folder / f"{survey_id}_respondents.json", "w") as f:
            json.dump(respondent_data, f, indent=4, ensure_ascii=False)
