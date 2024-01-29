from typing import Union, AnyStr

from telegraph.aio import Telegraph
from telegraph_pages.text_blueprints import get_executor_summary
from database_api.components.reviews import Reviews, UserReviewResponse
from database_api.components.executors import Executors, ExecutorModel


async def get_summary_url(reviews: UserReviewResponse):
    telegraph = Telegraph()
    profile_name = reviews.pos_sights[0].username
    executor_desc = None
    executor: ExecutorModel = await Executors().get_executor_data(reviews.pos_sights[0].reviewed_id).do_request()
    if isinstance(executor, ExecutorModel):
        executor_desc = executor.description

    await telegraph.create_account(short_name="dealbot")
    page = await telegraph.create_page(
        title=f"Відгуки для профілю - {profile_name}",
        html_content=get_executor_summary(
            positives=reviews.pos_sights,
            negatives=reviews.neg_sights,
            avg_rating=reviews.avg_rating,
            comments=reviews.comments,
            executor_desc=executor_desc
        )
    )
    return page["url"]


def create_executor_summary_text(link: str) -> AnyStr:
    return f'<a href="{link}">Посилання на відгуки про користувача</a>\n\n' if link else ""
