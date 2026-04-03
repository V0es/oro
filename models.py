import uuid
from enum import Enum
from sqlalchemy import String, ForeignKey, Enum as SqlEnum, Integer, Text, Uuid, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class QuestionType(int, Enum):
    TEXT = 1
    SINGLE = 2
    MULTIPLE = 3


class Survey(Base):
    __tablename__ = 'surveys'

    id: Mapped[str] = mapped_column(String(16), primary_key=True)

    questions: Mapped[list[Question]] = relationship('Question', back_populates='survey')
    respondents: Mapped[list[Respondent]] = relationship('Respondent', back_populates='survey')


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    survey_id: Mapped[str] = mapped_column(String(16), ForeignKey('surveys.id'))

    name: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(512))
    type: Mapped[QuestionType] = mapped_column(SqlEnum(QuestionType), nullable=False)

    survey: Mapped[Survey] = relationship('Survey', back_populates='questions')
    options: Mapped[list[Option]] = relationship('Option', back_populates='question')
    responses: Mapped[list[Response]] = relationship('Response', back_populates='question')


class Option(Base):
    __tablename__ = 'options'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('questions.id'))

    code: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    question: Mapped[Question] = relationship('Question', back_populates='options')


class Respondent(Base):
    __tablename__ = 'respondents'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    survey_id: Mapped[str] = mapped_column(String(16), ForeignKey('surveys.id'), nullable=False)

    survey: Mapped[Survey] = relationship('Survey', back_populates='respondents')
    responses: Mapped[list[Response]] = relationship('Response', back_populates='respondent')


class Response(Base):
    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(primary_key=True)
    respondent_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('respondents.id'), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('questions.id'), nullable=False)
    option_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('options.id'), nullable=True)
    order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    question: Mapped[Question] = relationship('Question', back_populates='responses')
    option: Mapped[Option | None] = relationship('Option')
    respondent: Mapped[Respondent] = relationship('Respondent', back_populates='responses')

    __table_args__ = (
        UniqueConstraint('respondent_id', 'question_id', 'option_id'),
    )
