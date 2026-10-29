import sqlite3
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query, status

from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=list[RecordRead], summary="Список записів")
def get_records(
    category_id: int | None = Query(None, gt=0),
    status_filter: Literal["new", "in_progress", "done"] | None = Query(
        None, alias="status"
    ),
    min_value: float | None = Query(None, ge=0, allow_inf_nan=False),
    q: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return repository.get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    summary="Отримати запис",
)
def get_record(record_id: int = Path(gt=0)):
    record = repository.get_record_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Запис не знайдено")

    return record


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити запис",
)
def create_record(payload: RecordCreate):
    try:
        return repository.create_record(**payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Запис із таким кодом уже існує",
        ) from error


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    summary="Повністю оновити запис",
)
def update_record(
    payload: RecordReplace,
    record_id: int = Path(gt=0),
):
    try:
        return repository.update_record(
            record_id=record_id,
            **payload.model_dump(),
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Запис не знайдено") from error
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Запис із таким кодом уже існує",
        ) from error


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити запис",
)
def delete_record(record_id: int = Path(gt=0)):
    if not repository.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Запис не знайдено")


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Пакетне створення записів",
)
def create_records_bulk(payload: list[RecordCreate]):
    if not 1 <= len(payload) <= 100:
        raise HTTPException(
            status_code=422,
            detail="Потрібно передати від 1 до 100 записів",
        )

    try:
        records = [item.model_dump() for item in payload]
        return repository.batch_create_records(records)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Дублікат коду в базі або в пакеті",
        ) from error
