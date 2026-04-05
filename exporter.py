import json
from collections import defaultdict
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from config import AggregationType, get_settings
from models import QuestionType, Respondent, Response, Survey

settings = get_settings()


def fetch_surveys_data(session: Session) -> Iterable[Survey]:
    """Получение данных из базы

    Args:
        session (Session): Объект сессии

    Returns:
        Iterable[Survey]: Объекты опросов с присоединёнными данными
    """
    stmt = (
        select(Survey)
        .options(
            selectinload(Survey.respondents)
            .selectinload(Respondent.responses)
            .joinedload(Response.question),
            selectinload(Survey.respondents)
            .selectinload(Respondent.responses)
            .joinedload(Response.option),
            selectinload(Survey.respondents)
            .selectinload(Respondent.responses)
            .joinedload(Response.respondent),
        )
        .order_by(Survey.id)
    )

    result = session.execute(stmt).scalars().all()
    return result


def respondent_transform(surveys: Iterable[Survey]) -> dict:
    """Трансформация ORM объектов в словарь с аггрерацией по респондентам

    Args:
        surveys (Iterable[Survey]): Объекты опросов

    Returns:
        dict: Итоговый объект
    """

    result = {}
    for survey in surveys:
        survey_data = {}
        for respondent in survey.respondents:
            respondent_data = {}
            responses_agg = defaultdict(list)

            for response in respondent.responses:
                responses_agg[response.question.name].append(response)

            for response_group in responses_agg.values():
                question = response_group[0].question
                question_data = {}
                question_data["type"] = question.type.name
                question_data["text"] = question.text
                if question.type == QuestionType.TEXT:
                    question_data["answer"] = response_group[0].text

                elif question.type == QuestionType.SINGLE:
                    question_data["answer"] = {
                        "code": response_group[0].option.code,
                        "label": response_group[0].option.text,
                    }

                elif question.type == QuestionType.MULTIPLE:
                    question_data["answer"] = [
                        {
                            "code": response.option.code,
                            "label": response.option.text,
                            "order": response.order,
                        }
                        for response in sorted(response_group, key=lambda r: r.order)
                    ]

                respondent_data[question.name] = question_data

            survey_data[str(respondent.id)] = respondent_data
        result[str(survey.id)] = survey_data
    return result


def question_transform(surveys: Iterable[Survey]) -> dict:
    """
    Трансформация ORM объектов в словарь с аггрерацией по вопросам

    Args:
        surveys (Iterable[Survey]): Объекты опросов

    Returns:
        dict: Итоговый объект
    """
    result = {}

    for survey in surveys:
        survey_data = {}

        questions_map = defaultdict(list)

        for respondent in survey.respondents:
            for response in respondent.responses:
                questions_map[response.question].append(response)

        for question, responses in questions_map.items():
            responses_agg = defaultdict(list)

            for r in responses:
                responses_agg[r.respondent_id].append(r)

            respondent_data = {}

            for response_group in responses_agg.values():
                r0 = response_group[0]

                if question.type == QuestionType.TEXT:
                    answer = r0.text

                elif question.type == QuestionType.SINGLE:
                    answer = {
                        "code": r0.option.code,
                        "label": r0.option.text,
                    }

                else:
                    answer = [
                        {
                            "code": r.option.code,
                            "label": r.option.text,
                            "order": r.order,
                        }
                        for r in sorted(response_group, key=lambda x: x.order)
                    ]

                respondent_data[str(r0.respondent.id)] = answer

            survey_data[question.name] = {
                "type": question.type.name,
                "text": question.text,
                "respondents": respondent_data,
            }

        result[str(survey.id)] = survey_data

    return result


def save_data_to_json(survey_data: dict, agg_type: AggregationType):
    """Сохраниение выходных данных в json файлы

    Args:
        survey_data (dict): Аггрегированный объект опросов
        agg_type (AggregationType): Тип аггрегации (по респондентам или по вопросам)
    """
    folder_path = (
        settings.output.respondents_folder
        if agg_type == AggregationType.RESPONDENTS
        else settings.output.questions_folder
    )
    for survey_id, data in survey_data.items():
        with open(
            folder_path / f"{survey_id}_{agg_type.value}.json",
            "w",
        ) as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
