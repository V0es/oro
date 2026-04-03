from pathlib import Path

from openpyxl import load_workbook

from models import Respondent, Response


def parse_excel_file(filepath: Path) -> tuple[list[Respondent], list[Response]]:
    wb = load_workbook(filepath)
    rows = wb["Sheet"].rows
    headers = [str(cell.value) for cell in next(rows)]

    respondents = {}
    responses = []

    for row in rows:
        row_d = {
            key: value for key, value in zip(headers, [cell.value for cell in row])
        }
        survey_id = row_d["survey"]
        respondent_id = row_d["respondent"]
        question_id = row_d["question"]
        response_id = row_d["response"]
        order = int(str(row_d["order"])) if row_d["order"] else None
        text = row_d["text"]

        # surveys.add(Survey(id=survey_id))
        if respondent_id not in respondents:
            respondents[respondent_id] = Respondent(
                id=respondent_id, survey_id=survey_id
            )

        responses.append(
            Response(
                respondent_id=respondent_id,
                question_id=question_id,
                option_id=response_id,
                order=order,
                text=text,
            )
        )

    return list(respondents.values()), responses
