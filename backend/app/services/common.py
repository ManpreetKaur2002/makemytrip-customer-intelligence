from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def commit_or_raise(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "The record conflicts with an existing record or database constraint."
        ) from error
