"""Aggregate API router."""
from fastapi import APIRouter
from app.api import upload, analyze, references, chat

router = APIRouter()

router.include_router(upload.router, tags=["Document Upload"])
router.include_router(analyze.router, tags=["Analysis"])
router.include_router(references.router, tags=["Reference Validation"])
router.include_router(chat.router, tags=["Chat"])
