from config import AggregationType, get_settings
from database import get_session
from exporter import (
    fetch_surveys_data,
    question_transform,
    respondent_transform,
    save_data_to_json,
)
from loader import load_data_to_db

settings = get_settings()


def main():

    with get_session() as session:
        load_data_to_db(session=session)

        surveys = fetch_surveys_data(session=session)

        respondent_aggregation = respondent_transform(surveys)
        question_aggregation = question_transform(surveys)

    save_data_to_json(respondent_aggregation, AggregationType.RESPONDENTS)
    save_data_to_json(question_aggregation, AggregationType.QUESTIONS)


if __name__ == "__main__":
    main()
