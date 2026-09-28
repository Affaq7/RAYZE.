from fastapi import APIRouter

from app.api.v1 import careers, contact, portfolio, reviews

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(portfolio.public_router)
api_router.include_router(portfolio.admin_router)

api_router.include_router(reviews.public_router)
api_router.include_router(reviews.admin_router)

api_router.include_router(careers.public_router)
api_router.include_router(careers.admin_postings_router)
api_router.include_router(careers.admin_applications_router)

api_router.include_router(contact.public_router)
api_router.include_router(contact.admin_router)
