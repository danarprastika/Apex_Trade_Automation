from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check(response: Response) -> dict:
    response.status_code = 200
    return {"status": "healthy"}
