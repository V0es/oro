from config import get_settings
from database import get_session
from exporter import convert_data_to_dict, fetch_survey_data, save_jsons
from loader import load_data_to_db

settings = get_settings()


def main():

    with get_session() as session:
        load_data_to_db(session=session)

        data_rows = fetch_survey_data(session=session)
        data_object = convert_data_to_dict(rows=data_rows)

        save_jsons(data_object)


if __name__ == "__main__":
    main()
