from typing import Optional, List

from database_api.base import BaseAPI, HttpMethod
from pydantic import BaseModel


class UserSights(BaseModel):
    username: str
    reviewed_id: int
    sight_title: str
    count: int

    def __str__(self):
        reviewed, people = ("відмітило", "людей") if self.count > 1 else ("відмітила", "людина")
        return f"{self.sight_title} - {reviewed} {self.count} {people}"


class UserComments(BaseModel):
    username: str
    comment: str


class UserReviewResponse(BaseModel):
    pos_sights: List[UserSights]
    neg_sights: List[UserSights]
    avg_rating: str
    comments: List[UserComments]


class Reviews(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/reviews"

    def save_review_data(self, reviewer_id: int, reviewed_id: int, task_id: int, rating: int, comment: str = None,
                         positive_sights: List[str] = None, negative_sights: List[str] = None):
        url = f"{self.component_path}/"
        json = {
            "reviewer_id": reviewer_id,
            "reviewed_id": reviewed_id,
            "task_id": task_id,
            "rating": rating,
            "positive_sights": positive_sights,
            "negative_sights": negative_sights,
            "comment": comment
        }
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_user_reviews(self, user_id: int):
        url = f"{self.component_path}/{user_id}"
        self.response_model = UserReviewResponse
        return self._construct_params(method=HttpMethod.GET, url=url)
