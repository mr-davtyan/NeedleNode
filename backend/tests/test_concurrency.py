import pytest
import threading
import time
from unittest.mock import patch
from backend.state import scan_state, import_state
from backend.database import SessionLocal, SystemState

def test_state_sync_concurrency(db):
    """
    Test that multiple 'threads' can update the state via the DBProxy without loss.
    """
    # Ensure rows exist
    scan_state.reset()
    import_state.reset()
    
    def update_task(state_proxy, iterations):
        for i in range(iterations):
            # Use atomic increment to avoid race conditions
            state_proxy.increment_processed()
            
    threads = []
    # 5 threads, each incrementing 20 times = 100 total
    for _ in range(5):
        t = threading.Thread(target=update_task, args=(scan_state, 20))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert scan_state.processed == 100

def test_wal_mode_concurrent_access(db):
    """
    Test WAL mode by performing concurrent reads and writes.
    SQLite in WAL mode should handle this without 'database is locked'.
    """
    from backend.database import File
    
    def writer():
        for i in range(50):
            with SessionLocal() as session:
                f = File(name=f"write_{i}.pes", path=f"lib/write_{i}.pes", size=i)
                session.add(f)
                session.commit()
            time.sleep(0.01)

    def reader():
        for _ in range(100):
            with SessionLocal() as session:
                _ = session.query(File).count()
            time.sleep(0.005)

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=reader)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # If no exception was raised, WAL is doing its job.
    with SessionLocal() as session:
        assert session.query(File).filter(File.name.like("write_%")).count() == 50
