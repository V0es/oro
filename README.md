## Задание
### Требования
- uv
- запущенная база PostgreSQL

### Запуск кода

1. Склонировать репозиторий
```bash
git clone git@github.com:V0es/oro.git

cd oro
```

2. Установить зависимости
```bash
uv sync
```

3. Сконфигурировать переменные окружения из `.env.example` или использовать по умолчанию
```bash
DATABASE__HOST =
DATABASE__PORT =
DATABASE__USERNAME =
DATABASE__PASSWORD =
DATABASE__NAME =

XML__CATEGORIES_PATH =
XML__QUESTION_PATH =
```

4. Запустить
```bash
uv run main.py
```