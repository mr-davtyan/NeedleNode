import time
import os
from backend.scanner import process_file
from backend.database import SessionLocal, init_db

def benchmark(count=10):
    init_db()
    db = SessionLocal()
    
    start_time = time.time()
    processed = 0
    
    for root, _, files in os.walk("library"):
        for file in files:
            if file.lower().endswith(".pes"):
                file_path = os.path.join(root, file)
                if process_file(file_path, db):
                     processed += 1
                if processed >= count:
                     break
        if processed >= count:
             break
             
    end_time = time.time()
    elapsed = end_time - start_time
    avg_per_file = elapsed / count if count > 0 else 0
    
    print(f"Benchmark: Processed {count} files in {elapsed:.2f} seconds.")
    print(f"Average time per file: {avg_per_file:.4f} seconds.")
    print(f"Estimated time for 10,000 files: {avg_per_file * 10000 / 60:.2f} minutes.")
    
    db.close()

if __name__ == "__main__":
    benchmark(10)
