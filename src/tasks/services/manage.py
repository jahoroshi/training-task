from datetime import datetime, UTC

from fastapi import HTTPException

from logger import logger
from src.tasks.worker import send_email_task


class TaskService:
    def __init__(self, task_repo):
        self.task_repo = task_repo


    async def add(self, task_data, current_user, session):
        task_dict = task_data.model_dump()
        task_dict['user'] = current_user
        task_dict['created_at'] = datetime.now(UTC)
        task = await self.task_repo.create_task(task_dict, session)

        email = current_user.email
        eta = task_dict['datetime_to_do']
        text = task_dict['task_info']
        try:
            send_email_task.apply_async((email, text), eta=eta)
        except Exception as e:
            logger.info(f"Notification not created. {e}")

        return task

    async def update(self, task_id, task_data, current_user, session):
        task = await self.task_repo.get_task(task_id, current_user, session)

        if not task:
            raise HTTPException(status_code=404, detail='Task not found')

        new_data = task_data.dict(exclude_unset=True, exclude_none=True)
        new_data['updated_at'] = datetime.now(UTC)

        updated_task = await self.task_repo.update_task(task, new_data, session)

        return updated_task



    async def get_task(self, task_id, current_user, session):
        task = await self.task_repo.get_task(task_id, current_user, session)
        if task is None:
            raise HTTPException(status_code=404, detail='Task not found')
        return task


    async def get_list(self, current_user, session):
        return await self.task_repo.get_task_list(current_user, session)
