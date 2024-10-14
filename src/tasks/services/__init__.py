from src.tasks.services.manage import TaskService
from src.tasks.services.repository import TaskRepository


task_service = TaskService(TaskRepository())
