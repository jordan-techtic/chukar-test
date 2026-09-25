"""Activity data access repository."""

import uuid
from datetime import date

from sqlalchemy import and_, extract, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.activity import Activity


class ActivityRepository:
    """Encapsulates database queries for Activity records."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active SQLAlchemy session."""
        self._db = db

    def get_by_id(self, activity_id: uuid.UUID) -> Activity | None:
        """Return an activity by primary key."""
        return self._db.get(Activity, activity_id)

    def get_by_date_and_type(self, activity_date: date, activity_type: str) -> Activity | None:
        """Return an activity matching date and type."""
        statement = select(Activity).where(
            and_(
                Activity.activity_date == activity_date,
                Activity.activity_type == activity_type,
            )
        )
        return self._db.scalar(statement)

    def list_by_year(
        self,
        year: int,
        month: int | None = None,
        status: str | None = "active",
    ) -> list[Activity]:
        """Return activities for a calendar year, optionally filtered by month."""
        conditions = [extract("year", Activity.activity_date) == year]
        if month is not None:
            conditions.append(extract("month", Activity.activity_date) == month)
        if status is not None:
            conditions.append(Activity.status == status)

        statement = (
            select(Activity)
            .where(and_(*conditions))
            .order_by(Activity.activity_date, Activity.title)
        )
        return list(self._db.scalars(statement).all())

    def create(self, activity: Activity) -> Activity:
        """Persist a new activity record."""
        self._db.add(activity)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise exc
        self._db.refresh(activity)
        return activity

    def update(self, activity: Activity) -> Activity:
        """Persist changes to an existing activity record."""
        self._db.add(activity)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise exc
        self._db.refresh(activity)
        return activity

    def delete(self, activity: Activity) -> None:
        """Remove an activity record."""
        self._db.delete(activity)
        self._db.commit()
