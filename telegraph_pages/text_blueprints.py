from typing import List, Optional

from database_api.components.reviews import UserSights, UserComments


def get_executor_summary(positives: List[UserSights], negatives: List[UserSights], avg_rating: str,
                         comments: List[UserComments], executor_desc: Optional[str] = None):
    pos_sights = [f"<li>{pos}</li>" for pos in positives]
    neg_sights = [f"<li>{neg}</li>" for neg in negatives]
    coms = [f"<p>` <i>{com.comment.capitalize()}</i> ` - <b>@{com.username}</b></p>" for com in comments]

    pos_sights = "".join(pos_sights)
    neg_sights = "".join(neg_sights)
    coms = "".join(coms)
    desc = f"<p>Опис: {executor_desc}</p>" if executor_desc else ""

    return (f"{desc}"
            f"<p>Середній Рейтинг: {avg_rating} з 5 ⭐</p><p><b>Позитивні Відгуки:</b></p></br>"
            f"<ul>{pos_sights}</ul><p><b>Негативні Відгуки:</b></p></br><ul>{neg_sights}</ul>"
            f"<p><b>Письмові відгуки від користувачів:</b></p>{coms}")
