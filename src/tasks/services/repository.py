from sqlalchemy import select

from models import Task


class TaskRepository:
    async def create_task(self, task_dict, session):
        task = Task(**task_dict)
        session.add(task)
        await session.commit()
        return task

    async def get_task(self, task_id, current_user, session):
        query = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        return task

    async def get_task_list(self, current_user, session):
        query = select(Task).where(Task.user_id == current_user.id)
        result = await session.execute(query)
        tasks = result.scalars().all()
        return tasks

    async def update_task(self, task, new_data, session):

        if new_data:
            for key, value in new_data.items():
                setattr(task, key, value)

        await session.commit()

        return task