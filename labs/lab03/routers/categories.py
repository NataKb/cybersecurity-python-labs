from fastapi import APIRouter, HTTPException, Path, status

from labs.lab03 import repository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead], summary="Список категорій")
def get_categories():
    return repository.get_categories()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити категорію",
)
def create_category(payload: CategoryCreate):
    try:
        return repository.create_category(payload.name)
    except Exception as error:
        import sqlite3

        if isinstance(error, sqlite3.IntegrityError):
            raise HTTPException(
                status_code=409,
                detail="Категорія з такою назвою вже існує",
            ) from error
        raise


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити порожню категорію",
)
def delete_category(category_id: int = Path(gt=0)):
    try:
        deleted = repository.delete_empty_category(category_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if not deleted:
        raise HTTPException(status_code=404, detail="Категорію не знайдено")
