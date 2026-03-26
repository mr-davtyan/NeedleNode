import pytest
import time
from datetime import datetime, timedelta
from backend.state import scan_state, import_state
from backend.database import SessionLocal, SystemState

def test_heartbeat_update(db):
    """Test that heartbeat() updates the timestamp in the database."""
    scan_state.reset()
    initial_heartbeat = None
    
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        initial_heartbeat = row.last_heartbeat
        
    time.sleep(0.1)
    scan_state.heartbeat()
    
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        assert row.last_heartbeat > initial_heartbeat

def test_staleness_detection_and_reset(db):
    """Test that is_scanning returns False and resets state if heartbeat is old."""
    scan_state.reset()
    
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        row.is_active = True
        # Set heartbeat to 60 seconds ago
        row.last_heartbeat = datetime.utcnow() - timedelta(seconds=60)
        session.commit()
        
    # Standard getter should now detect staleness and return False
    assert scan_state.is_scanning is False
    
    # Check that it actually reset it in the DB too
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        assert row.is_active is False

def test_active_heartbeat_not_reset(db):
    """Test that a fresh heartbeat prevents the state from being reset."""
    scan_state.reset()
    scan_state.is_scanning = True # This sets heartbeat to NOW
    
    # Verify it is active
    assert scan_state.is_scanning is True
    
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        assert row.is_active is True

def test_setter_updates_heartbeat(db):
    """Test that setting is_active=True automatically updates the heartbeat."""
    scan_state.reset()
    
    # Manually set an old heartbeat while inactive
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        row.last_heartbeat = datetime.utcnow() - timedelta(seconds=60)
        session.commit()
    
    # Setting to True should refresh heartbeat
    scan_state.is_scanning = True
    
    with SessionLocal() as session:
        row = session.query(SystemState).filter(SystemState.key == 'scan').first()
        # Should be within the last few seconds
        assert (datetime.utcnow() - row.last_heartbeat).total_seconds() < 5
