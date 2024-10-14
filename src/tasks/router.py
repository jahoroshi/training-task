from typing import List

from fastapi import APIRouter, Depends

from database import get_session
from src.auth.services import token_service
from src.tasks.schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema
from src.tasks.services import task_service

router = APIRouter(
    prefix='/tasks',
    tags=['Tasks']
)


@router.post(
    '/add',
    response_model=TaskSchema,
    description="Создает новую задачу.",
    responses={
        201: {"description": "Задача успешно создана."},
        401: {"description": "Не авторизован."},
        422: {"description": "Ошибка в валидации."}
    }
)
async def add_task(task_data: TaskCreateSchema,
                   current_user=Depends(token_service.get_current_user),
                   session=Depends(get_session)):
    return await task_service.add(task_data, current_user, session)


@router.patch(
    '/{task_id}/update',
    response_model=TaskSchema,
    description="Обновляет существующую задачу.",
    responses={
        200: {"description": "Задача успешно обновлена."},
        400: {"description": "Некорректные данные."},
        401: {"description": "Не авторизован."},
        404: {"description": "Задача не найдена."}
    }
)
async def update_task(task_id: int, task_data: TaskUpdateSchema,
                      current_user=Depends(token_service.get_current_user), session=Depends(get_session)):
    return await task_service.update(task_id, task_data, current_user, session)


@router.get(
    '/list',
    response_model=List[TaskSchema],
    description="Получает все задачи пользователя.",
    responses={
        200: {"description": "Список задач получен."},
        401: {"description": "Не авторизован."}
    })
async def get_task_list(current_user=Depends(token_service.get_current_user), session=Depends(get_session)):
    return await task_service.get_list(current_user, session)


@router.get(
    '/{task_id}',
    response_model=TaskSchema,
    description="Получает существующую задачу.",
    responses={
        200: {"description": "Задача успешно получена."},
        401: {"description": "Не авторизован."},
        404: {"description": "Задача не найдена."}
    })
async def get_task(task_id: int, current_user=Depends(token_service.get_current_user), session=Depends(get_session)):
    return await task_service.get_task(task_id, current_user, session)
