from logging import getLogger
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Company as CompanyModel
from app.models import row2dict
from app.schemas import CompanyCreate

logger = getLogger()


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_company_by_id(self, company_id: int) -> CompanyModel | None:
        """
        Retrieve a company by its ID if active.
        Args:
            company_id: ID of the company to retrieve.
        Returns:
            The company if found and active.
        Raises:
            HTTPException: If the company is not found.
        """
        company = await self.db.scalar(
            select(CompanyModel).where(
                CompanyModel.id == company_id, CompanyModel.active.is_(True)
            )
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    async def get_all_companies(self) -> Sequence[CompanyModel]:
        """
        Retrieve all companies from the database.
        Returns:
            List of all companies.
        """
        companies = await self.db.scalars(select(CompanyModel))
        return companies.all()

    async def add_company(self, company: CompanyCreate) -> dict:
        """
        Add a new company to the database.
        Args:
            company: Company details to be added.
        Returns:
            dict: Newly added company as a dictionary.
        Raises:
            HTTPException: If a company with the same name already exists.
        """
        db_company = CompanyModel(**company.model_dump())
        self.db.add(db_company)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            logger.error(
                "EXCEPTION ADDING_COMPANY_IN_DB WRT company_id %s: %s",
                company.name,
                exc,
            )
            raise HTTPException(
                status_code=400, detail="Another company with same name already exists"
            )
        await self.db.refresh(db_company)
        return row2dict(db_company)

    async def update_company_details(
        self, company_id: int, company: CompanyCreate
    ) -> dict | None:
        """
        Update a company's details by ID.
        Args:
            company_id: Company ID to update.
            company: New company details.
        Returns:
            dict: Updated company as a dictionary, or None if not found.
        """
        db_company = await self.get_company_by_id(company_id)
        if db_company:
            for key, value in company.model_dump().items():
                setattr(db_company, key, value)
            await self.db.commit()
            await self.db.refresh(db_company)
        return row2dict(db_company)
