import xml.etree.ElementTree as ET
from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Option, Question, Respondent, Response, Survey


def parse_options(xml_tree_rool: ET.Element) -> list[Option]:
    options = []
    for categories in xml_tree_rool.findall("variables/categories"):
        question_id = categories.get("id")
        for category in categories.findall("category"):
            option_id = category.get("id")
            code = int(category.get("code"))
            text = category.text
            options.append(
                Option(id=option_id, question_id=question_id, code=code, text=text)
            )
    return options


def parse_questions(xml_tree_root: ET.Element, survey_id: str) -> list[Question]:
    questions = []
    for question in xml_tree_root.findall("metadata/questions/question"):
        id = question.get("id")
        type = int(question.get("type"))
        name = question.find("name").text
        text = question.find("text").text

        questions.append(
            Question(id=id, survey_id=survey_id, name=name, text=text, type=type)
        )
    return questions


def load_xml_file(filepath: Path, session: Session):
    tree = ET.parse(source=filepath)
    root = tree.getroot()
    survey_id = filepath.name.replace(".xml", "")
    options = parse_options(root)
    questions = parse_questions(xml_tree_root=root, survey_id=survey_id)

    session.add_all(options)
    session.add_all(questions)

    session.commit()


def load_xml_folder(folder_path: Path, session: Session):
    for file in folder_path.glob("*.xml"):
        load_xml_file(filepath=file, session=session)


def load_excel(filepath: Path, session: Session):
    wb = load_workbook(filepath)
    rows = wb["Sheet"].rows
    headers = [str(cell.value) for cell in next(rows)]

    surveys = []
    respondents = set()
    responses = []

    for row in rows:
        row_d = {
            key: value for key, value in zip(headers, [cell.value for cell in row])
        }
        survey_id = row_d["survey"]
        respondent_id = row_d["respondent"]
        question_id = row_d["question"]
        response_id = row_d["response"]
        order = int(row_d.get("order"))
        text = row_d["text"]

        surveys.append(Survey(id=survey_id))

        respondents.add(Respondent(id=respondent_id, survey_id=survey_id))
        if response_id:
            responses.append(
                Response(
                    respondent_id=respondent_id,
                    question_id=question_id,
                    option_id=response_id,
                    order=order,
                    text=text,
                )
            )

        session.add_all(surveys)
        session.add_all(respondents)
        session.add_all(responses)

        session.commit()


def main():
    engine = create_engine("")

    with Session(engine) as session:
        load_xml_folder(Path())
