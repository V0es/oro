import xml.etree.ElementTree as ET
from pathlib import Path

from config import get_settings
from models import Option, Question, Survey

settings = get_settings()


def parse_options(xml_tree_rool: ET.Element) -> list[Option]:
    options = []
    for categories in xml_tree_rool.findall(settings.xml.categories_path):
        question_id = categories.get("id")
        for category in categories.findall("category"):
            option_id = category.get("id")
            raw_code = category.get("code")
            code = int(raw_code) if raw_code is not None else None
            text = category.text
            options.append(
                Option(id=option_id, question_id=question_id, code=code, text=text)
            )
    return options


def parse_questions(xml_tree_root: ET.Element, survey_id: str) -> list[Question]:
    questions = []
    for question in xml_tree_root.findall(settings.xml.question_path):
        id = question.get("id")

        raw_type = question.get("type")

        type = int(raw_type) if raw_type is not None else None

        name_tag = question.find("name")
        text_tag = question.find("text")
        name = name_tag.text if name_tag is not None else None
        text = text_tag.text if text_tag is not None else None

        questions.append(
            Question(id=id, survey_id=survey_id, name=name, text=text, type=type)
        )
    return questions


def parse_xml_file(filepath: Path):
    tree = ET.parse(source=filepath)
    root = tree.getroot()
    survey_id = filepath.name.replace(".xml", "")
    survey = Survey(id=survey_id)
    options = parse_options(root)
    questions = parse_questions(xml_tree_root=root, survey_id=survey_id)

    return options, questions, survey


def parse_xml_folder(
    folder_path: Path,
) -> tuple[list[Option], list[Question], list[Survey]]:
    options = []
    questions = []
    surveys = []
    for file in folder_path.glob("*.xml"):
        options_partition, questions_partition, survey = parse_xml_file(filepath=file)
        options.extend(options_partition)
        questions.extend(questions_partition)
        surveys.append(survey)
    return options, questions, surveys
