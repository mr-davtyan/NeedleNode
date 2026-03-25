import os
import shutil
from backend.classify_inbox import get_unique_target_path

def test_deduplication():
    print("--- Starting Deduplication Tests ---")
    LIBRARY_DIR = "test_library"
    main_tag = "Animal"
    sub_tags_str = "bear,cute"
    orig_name_clean = "design"
    orig_ext = ".pes"

    # Setup mock files
    target_dir = os.path.join(LIBRARY_DIR, main_tag)
    if os.path.exists(LIBRARY_DIR):
         shutil.rmtree(LIBRARY_DIR)
    os.makedirs(target_dir, exist_ok=True)

    # Test 1: No collision
    path, filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
    print(f"Test 1 (No Collision): {filename}")
    assert filename == "Animal (bear,cute) design.pes", f"Expected 'Animal (bear,cute) design.pes', got '{filename}'"

    # Create file for Test 2
    open(path, 'w').close()

    # Test 2: Single collision
    path, filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
    print(f"Test 2 (1 Collision): {filename}")
    assert filename == "Animal (bear,cute) design_1.pes", f"Expected 'Animal (bear,cute) design_1.pes', got '{filename}'"

    # Create second file for Test 3
    open(path, 'w').close()

    # Test 3: Multiple collisions
    path, filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
    print(f"Test 3 (2 Collisions): {filename}")
    assert filename == "Animal (bear,cute) design_2.pes", f"Expected 'Animal (bear,cute) design_2.pes', got '{filename}'"

    # Cleanup
    shutil.rmtree(LIBRARY_DIR)
    print("--- All Deduplication Tests Passed! ---")

if __name__ == "__main__":
    test_deduplication()
