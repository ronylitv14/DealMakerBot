from datetime import date
from typing import List

from utils.dialog_categories import university_tasks, subject_titles


def create_group_message(
        task_status,
        task_price,
        task_types: List[str],
        task_subjects: List[str],
        task_description: str,
        task_deadline: date,
):
    # task_subjects = [task_subject.replace(" ", "_") for task_subject in task_subjects]
    # task_types = [task_type.replace(" ", "_") for task_type in task_types]

    # subjects_str = "#" + " #".join([subject_titles[int(t)][0].replace(" ", "_") for t in task_subjects])
    # types_str = "#" + " #".join([university_tasks[int(t)][0].replace(" ", "_") for t in task_types])

    types_str = "#" + " #".join([task_type.replace(" ", "_") for task_type in task_types])
    subjects_str = "#" + " #".join([task_subject.replace(" ", "_") for task_subject in task_subjects])

    message = f"🟢{task_status}\n\n{types_str}\n{subjects_str}\n\nОпис:\n{task_description}\n\nЦіна: {task_price}\n\nДедлайн: {task_deadline}\n"
    return message

