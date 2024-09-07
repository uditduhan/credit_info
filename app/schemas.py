from datetime import date
from enum import Enum
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, EmailStr, HttpUrl, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber


def http_value_to_string(value: HttpUrl) -> str:
    return str(value)


URLStr = Annotated[HttpUrl, AfterValidator(http_value_to_string)]


class LoanStatus(str, Enum):
    PAID = "PAID"
    DUE = "DUE"
    INITIATED = "INITIATED"


class CompanyBase(BaseModel):
    name: str
    address: str
    registration_date: date
    employee_count: int
    contact_number: PhoneNumber
    contact_email: EmailStr
    website: Optional[URLStr]


class CompanyCreate(CompanyBase):
    @field_validator("name")
    @classmethod
    def name_validator(cls, value: str):
        assert value
        return value


class AnnualInformationBase(BaseModel):
    annual_turnover: float
    profit: float
    fiscal_year: str
    reported_date: date


class AnnualInformationCreate(AnnualInformationBase):
    pass


class LoanInformationBase(BaseModel):
    loan_amount: float
    taken_on: date
    bank_provider: str
    loan_status: LoanStatus


class LoanInformationCreate(LoanInformationBase):
    company_id: str


class LoanInformationUpdate(LoanInformationBase):
    id: int
