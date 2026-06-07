from datetime import datetime
from backend.database import SessionLocal, SystemState

class DBStateProxy:
    """
    A proxy that syncs state to the database instead of using local variables.
    This allows multiple Gunicorn worker processes to share the same status.
    """
    def __init__(self, key):
        self._key = key

    def _get_row(self, session):
        row = session.query(SystemState).filter(SystemState.key == self._key).first()
        if not row:
            # Should have been created by init_db, but fail-safe here
            row = SystemState(key=self._key, last_heartbeat=datetime.utcnow())
            session.add(row)
            session.commit()
            session.refresh(row)
        return row

    def heartbeat(self):
        """Updates the last_heartbeat timestamp for the current state."""
        with SessionLocal() as session:
            row = self._get_row(session)
            row.last_heartbeat = datetime.utcnow()
            session.commit()

    def _check_staleness(self, row, session):
        """
        If is_active is True but heartbeat is older than 30s, reset to False.
        Returns True if the state was reset.
        """
        if row.is_active:
            delta = (datetime.utcnow() - row.last_heartbeat).total_seconds()
            if delta > 30:
                row.is_active = False
                session.commit()
                return True
        return False

    @property
    def is_scanning(self):
        with SessionLocal() as session:
            row = self._get_row(session)
            self._check_staleness(row, session)
            return row.is_active
    
    @is_scanning.setter
    def is_scanning(self, value):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.is_active = value
            if value:
                row.last_heartbeat = datetime.utcnow()
            session.commit()

    @property
    def is_importing(self):
        with SessionLocal() as session:
            row = self._get_row(session)
            self._check_staleness(row, session)
            return row.is_active
    
    @is_importing.setter
    def is_importing(self, value):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.is_active = value
            if value:
                row.last_heartbeat = datetime.utcnow()
            session.commit()

    @property
    def processed(self):
        with SessionLocal() as session:
            return self._get_row(session).processed
    
    @processed.setter
    def processed(self, value):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.processed = value
            session.commit()

    def increment_processed(self, delta=1):
        with SessionLocal() as session:
            session.query(SystemState).filter(SystemState.key == self._key).update(
                {SystemState.processed: SystemState.processed + delta}
            )
            session.commit()

    @property
    def total(self):
        with SessionLocal() as session:
            return self._get_row(session).total
    
    @total.setter
    def total(self, value):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.total = value
            session.commit()

    @property
    def current_file(self):
        with SessionLocal() as session:
            return self._get_row(session).current_file
    
    @current_file.setter
    def current_file(self, value):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.current_file = value
            session.commit()

    @property
    def stop_requested(self):
        with SessionLocal() as session:
            return self._get_row(session).stop_requested
    
    @stop_requested.setter
    def stop_requested(self, value):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.stop_requested = value
            session.commit()

    def reset(self):
        with SessionLocal() as session:
            row = self._get_row(session)
            row.is_active = False
            row.processed = 0
            row.total = 0
            row.current_file = ""
            row.stop_requested = False
            row.last_heartbeat = datetime.utcnow()
            session.commit()

# Singleton instances (Proxies)
scan_state = DBStateProxy('scan')
import_state = DBStateProxy('import')
