import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies.core import DBSessionDep
from app.crud.company import CompanyRepository
from app.crud.credit import CreditRepository
from app.schemas import LoanInformationCreate, LoanInformationUpdate

router = APIRouter()


@router.get("/credits")
async def get_credit_info_of_all_company(db: DBSessionDep) -> JSONResponse:
    """
    Retrieve credit information for all companies.
    Args:
        db: Dependency for database session.
    Returns:
        A JSONResponse containing the credit information for each company, including:
        - company_id
        - company_name
        - credit_information (calculated as two-year turnover minus due amount)
    """
    company_repo = CompanyRepository(db)
    credit_repo = CreditRepository(db)
    companies = await company_repo.get_all_companies()
    company_ids = [company.id for company in companies]
    companies_turnover, companies_due_amount = await asyncio.gather(
        credit_repo.get_two_year_turnover_of_companies(company_ids),
        credit_repo.get_total_due_amount_of_companies(company_ids),
        return_exceptions=True,
    )
    result = []
    for company in companies:
        result.append(
            {
                "company_id": company.id,
                "company_name": company.name,
                "credit_information": round(
                    companies_turnover.get(company.id, 0)
                    - companies_due_amount.get(company.id, 0),
                    2,
                ),
            }
        )

    return JSONResponse({"data": result, "success": True}, status_code=200)


@router.get("/credits/{company_id}")
async def get_credit_info_of_a_company(
    company_id: str, db: DBSessionDep
) -> JSONResponse:
    """
    Retrieve credit information for a specific company.
    Args:
        company_id: The ID of the company to retrieve information for.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - company_id
        - company_name
        - credit_information (calculated as two-year turnover minus total due amount)
    """
    credit_repo = CreditRepository(db)
    company_repo = CompanyRepository(db)
    company_info = await company_repo.get_company_by_id(company_id)
    two_year_turnover, total_due_amount = await asyncio.gather(
        credit_repo.get_company_two_year_turnover(company_id),
        credit_repo.get_total_due_loan_amount(company_id),
        return_exceptions=True,
    )
    data = {
        "company_id": company_id,
        "company_name": company_info.name,
        "credit_information": round(two_year_turnover - total_due_amount, 2),
    }
    return JSONResponse({"data": data, "success": True}, status_code=200)


@router.post("/credits")
async def add_credit_info_for_a_company(
    loan: LoanInformationCreate, db: DBSessionDep
) -> JSONResponse:
    """
    Add loan information for a specific company.
    Args:
        loan: The loan information to add.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - data: The added loan information.
        - message: Success message.
        - success: Boolean indicating success.
    """
    company_repo = CompanyRepository(db)
    credit_repo = CreditRepository(db)
    await company_repo.get_company_by_id(loan.company_id)

    db_loan = await credit_repo.add_loans_of_company(loan)
    return JSONResponse(
        {"data": db_loan, "message": "Loan uploaded successfully", "success": True},
        status_code=201,
    )


@router.put("/credits/{company_id}")
async def update_credit_info(
    company_id: str, loan: LoanInformationUpdate, db: DBSessionDep
) -> JSONResponse:
    """
    Update loan details for a specific company.
    Args:
        company_id: The ID of the company.
        loan: The updated loan information.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - data: The updated loan information.
        - message: Success message.
        - success: Boolean indicating success.
    """
    company_repo = CompanyRepository(db)
    credit_repo = CreditRepository(db)
    await company_repo.get_company_by_id(company_id)

    db_loan = await credit_repo.update_loan_details_of_company(company_id, loan)
    return JSONResponse(
        {
            "data": db_loan,
            "message": "Loan details updated successfully",
            "success": True,
        },
        status_code=200,
    )


@router.delete("/credits/{loan_id}")
async def delete_loan_of_company(
    loan_id: int, company_id: str, db: DBSessionDep
) -> JSONResponse:
    """
    Soft deletes a loan for a specific company.
    Args:
        loan_id: The ID of the loan to be deleted.
        company_id: The ID of the company associated with the loan.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - message: Success message.
        - success: Boolean indicating success.
    """
    company_repo = CompanyRepository(db)
    credit_repo = CreditRepository(db)
    await company_repo.get_company_by_id(company_id)
    await credit_repo.delete_loan_of_company(company_id, loan_id)
    return JSONResponse(
        {"message": "Loan deleted successfully", "success": True}, status_code=200
    )
