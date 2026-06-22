from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.event import Event, EventEnrollment


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name, theme, organizer_id, start_date, end_date) -> Event:
        event = Event(
            name=name,
            theme=theme,
            organizer_id=organizer_id,
            start_date=start_date,
            end_date=end_date,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: int) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def list_all(self) -> List[Event]:
        return self.db.query(Event).all()

    def enroll_participant(self, event_id: int, participant_id: int) -> EventEnrollment:
        existing = self.db.query(EventEnrollment).filter(
            EventEnrollment.event_id == event_id,
            EventEnrollment.participant_id == participant_id
        ).first()
        if existing:
            return existing
        enrollment = EventEnrollment(event_id=event_id, participant_id=participant_id)
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_enrolled_events(self, participant_id: int) -> List[Event]:
        enrollments = self.db.query(EventEnrollment).filter(EventEnrollment.participant_id == participant_id).all()
        return [e.event for e in enrollments if e.event]
