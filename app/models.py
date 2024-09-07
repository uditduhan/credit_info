from datetime import date, datetime
from typing import Any

from nanoid import generate
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas import LoanStatus


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        index=True,
        insert_default=generate(alphabet="0123456789abcdefghijklmnopqrst", size=10),
    )
    name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    address: Mapped[str]
    registration_date: Mapped[date]
    employee_count: Mapped[int]
    contact_number: Mapped[str]
    contact_email: Mapped[str]
    website: Mapped[str]
    active: Mapped[bool] = mapped_column(insert_default=True)
    created_on: Mapped[date] = mapped_column(insert_default=datetime.now())
    updated_on: Mapped[date] = mapped_column(insert_default=datetime.now())


class AnnualInformation(Base):
    __tablename__ = "annual_information"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    annual_turnover: Mapped[float]
    profit: Mapped[float]
    fiscal_year: Mapped[str]
    reported_date: Mapped[date]
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"))
    active: Mapped[bool] = mapped_column(insert_default=True)
    created_on: Mapped[date] = mapped_column(insert_default=datetime.now())
    updated_on: Mapped[date] = mapped_column(insert_default=datetime.now())


class LoanInformation(Base):
    __tablename__ = "loan_information"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    loan_amount: Mapped[float]
    taken_on: Mapped[date]
    bank_provider: Mapped[str]
    loan_status: Mapped[LoanStatus]
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"))
    active: Mapped[bool] = mapped_column(insert_default=True)
    created_on: Mapped[date] = mapped_column(insert_default=datetime.now())
    updated_on: Mapped[date] = mapped_column(insert_default=datetime.now())


# class Users(Base):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
#     username: Mapped[str] = mapped_column(unique=True)
#     password: Mapped[str]


def row2dict(row: Any) -> dict:
    """
    Convert an SQLAlchemy model instance to a dictionary.
    Args:
        row: The SQLAlchemy model instance to convert.
    Returns:
        A dictionary where keys are column names and values are column values.
    """
    row_dict = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        if isinstance(value, date):
            value = datetime.strftime(value, "%y-%m-%d")
        row_dict[column.name] = value

    return row_dict
