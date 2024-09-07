from datetime import datetime
from logging import getLogger

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnnualInformation, LoanInformation, LoanStatus, row2dict
from app.schemas import LoanInformationCreate, LoanInformationUpdate, LoanStatus

logger = getLogger()


class CreditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_company_two_year_turnover(self, company_id: str) -> float:
        two_years_turnover = (
            select(AnnualInformation.annual_turnover)
            .where(AnnualInformation.company_id == company_id)
            .order_by(AnnualInformation.fiscal_year.desc())
            .limit(2)
            .subquery()
        )
        sum_of_turnovers = await self.db.scalar(
            func.sum(two_years_turnover.c.annual_turnover)
        )
        return sum_of_turnovers if sum_of_turnovers else 0.0

    async def get_total_due_loan_amount(self, company_id: str) -> float:
        due_amount = await self.db.scalar(
            select(func.sum(LoanInformation.loan_amount)).where(
                LoanInformation.company_id == company_id,
                LoanInformation.loan_status == LoanStatus.DUE.value,
            )
        )
        return due_amount if due_amount else 0.0

    async def get_two_year_turnover_of_companies(
        self, company_ids: list
    ) -> dict[str, float]:
        subquery = (
            select(
                AnnualInformation.company_id,
                AnnualInformation.annual_turnover,
                AnnualInformation.fiscal_year,
                func.row_number()
                .over(
                    partition_by=AnnualInformation.company_id,
                    order_by=AnnualInformation.fiscal_year.desc(),
                )
                .label("rank"),
            )
            .where(AnnualInformation.company_id.in_(company_ids))
            .subquery()
        )

        result = await self.db.execute(
            select(
                subquery.c.company_id,
                func.sum(subquery.c.annual_turnover).label("total_turnover"),
            )
            .where(subquery.c.rank <= 2)
            .group_by(subquery.c.company_id)
        )
        return {row.company_id: row.total_turnover for row in result.fetchall()}

    async def get_total_due_amount_of_companies(
        self, company_ids: list
    ) -> dict[str, float]:
        result = await self.db.execute(
            select(
                LoanInformation.company_id,
                func.sum(LoanInformation.loan_amount).label("due_amount"),
            )
            .where(
                LoanInformation.company_id.in_(company_ids),
                LoanInformation.loan_status == LoanStatus.DUE.value,
            )
            .group_by(LoanInformation.company_id)
        )
        return {row.company_id: row.due_amount for row in result.fetchall()}

    async def get_company_loan_by_id(
        self, company_id: str, loan_id: int
    ) -> LoanInformation:
        db_loan = await self.db.scalar(
            select(LoanInformation).where(
                LoanInformation.company_id == company_id, LoanInformation.id == loan_id
            )
        )
        if not db_loan:
            raise HTTPException(400, "Loan does not exist in the company")
        return db_loan

    async def add_loans_of_company(self, loan: LoanInformationCreate) -> dict:
        db_loans = LoanInformation(**loan.model_dump())
        self.db.add(db_loans)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            logger.error(
                "EXCEPTION ADDING_LOANS_OF_COMPANY_IN_DB WRT company_id %s: %s",
                loan.company_id,
                exc,
            )
            raise
        await self.db.refresh(db_loans)
        return row2dict(db_loans)

    async def update_loan_details_of_company(
        self, company_id: int, loan: LoanInformationUpdate
    ) -> dict:
        db_loan = await self.get_company_loan_by_id(company_id, loan.id)
        if db_loan:
            for key, value in loan.model_dump().items():
                setattr(db_loan, key, value)
            db_loan.updated_on = datetime.now()
            await self.db.commit()
            await self.db.refresh(db_loan)
        return row2dict(db_loan)

    async def delete_loan_of_company(self, company_id: str, loan_id: int) -> None:
        db_loan = await self.get_company_loan_by_id(company_id, loan_id)
        if db_loan:
            db_loan.active = False
            db_loan.updated_on = datetime.now()
            await self.db.commit()
            await self.db.refresh(db_loan)
