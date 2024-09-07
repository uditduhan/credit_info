from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies.core import DBSessionDep
from app.crud.company import CompanyRepository
from app.models import row2dict
from app.schemas import CompanyCreate

router = APIRouter()


@router.get("/company/{company_id}")
async def get_comany_details(company_id: str, db: DBSessionDep) -> JSONResponse:
    """
    Retrieve details of a specific company by ID.
    Args:
        company_id: The ID of the company to retrieve.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - data: The company's details as a dictionary.
        - success: Boolean indicating success.
    """
    company_crud = CompanyRepository(db)
    company_details = await company_crud.get_company_by_id(company_id)
    return JSONResponse({"data": row2dict(company_details), "success": True}, 200)


@router.post("/company")
async def create_company(company: CompanyCreate, db: DBSessionDep) -> JSONResponse:
    """
    Create a new company.
    Args:
        company: The company details to be created.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - data: The details of the created company.
        - message: A success message.
        - success: Boolean indicating success.
    """
    company_crud = CompanyRepository(db)
    company_details = await company_crud.add_company(company=company)
    return JSONResponse(
        {
            "data": company_details,
            "message": "Company created successfully",
            "success": True,
        },
        201,
    )


@router.put("/company/{company_id}")
async def update_company_details(
    company_id: str, company: CompanyCreate, db: DBSessionDep
) -> JSONResponse:
    """
    Update the details of an existing company.
    Args:
        company_id: The ID of the company to be updated.
        company: The new details of the company.
        db: Dependency for database session.
    Returns:
        A JSONResponse containing:
        - data: The updated company details.
        - message: A success message.
        - success: Boolean indicating success.
    """
    company_crud = CompanyRepository(db)
    company_details = await company_crud.update_company_details(company_id, company)
    return JSONResponse(
        {
            "data": company_details,
            "message": "Company details updated successfully",
            "success": True,
        },
        200,
    )
