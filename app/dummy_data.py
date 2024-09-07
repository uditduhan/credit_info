import random
from datetime import datetime

from faker import Faker
from nanoid import generate

from app.database import sessionmanager
from app.models import AnnualInformation, Company, LoanInformation

fake = Faker()


async def create_dummy_data() -> None:
    async with sessionmanager.session() as session:
        for _ in range(10):
            company_id = generate(alphabet="0123456789abcdefghijklmnopqrst", size=10)
            company = Company(
                id=company_id,
                name=fake.company(),
                address=fake.address(),
                registration_date=fake.date_between_dates(
                    datetime(2019, 1, 1), datetime(2020, 3, 31)
                ),
                employee_count=fake.random_int(min=10, max=500),
                contact_number=fake.basic_phone_number(),
                contact_email=fake.email(),
                website=fake.url(),
            )
            session.add(company)
            await session.commit()

            for year in range(2020, 2023):
                annual_info = AnnualInformation(
                    company_id=company_id,
                    annual_turnover=fake.pyfloat(
                        left_digits=7, right_digits=2, positive=True
                    ),
                    profit=fake.pyfloat(left_digits=6, right_digits=2, positive=True),
                    fiscal_year=f"{year}",
                    reported_date=datetime(year + 1, 3, 20).date(),
                )
                session.add(annual_info)

            for _ in range(random.randint(1, 5)):
                loan_info = LoanInformation(
                    company_id=company_id,
                    loan_amount=fake.pyfloat(
                        left_digits=7, right_digits=2, positive=True
                    ),
                    taken_on=fake.date_between_dates(
                        datetime(2020, 1, 1), datetime(2022, 12, 31)
                    ),
                    bank_provider=fake.company(),
                    loan_status=random.choice(["PAID", "DUE", "INITIATED"]),
                )
                session.add(loan_info)

        await session.commit()
