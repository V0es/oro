from sqlalchemy.orm import Session

from config import get_settings
from parsers.excel_parser import parse_excel_file
from parsers.xml_parser import parse_xml_folder

settings = get_settings()


def load_data_to_db(
    session: Session,
):

    respondents, responses = parse_excel_file(filepath=settings.xlsx.directory)
    options, questions, surveys = parse_xml_folder(folder_path=settings.xml.directory)

    session.add_all(surveys)
    session.add_all(questions)
    session.add_all(options)
    session.add_all(respondents)
    session.add_all(responses)

    session.commit()
