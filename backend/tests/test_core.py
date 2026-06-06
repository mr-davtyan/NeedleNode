import pytest
import os
from backend.scanner import extract_tags, should_keep_tag
from backend.classify_inbox import get_unique_target_path

def test_should_keep_tag():
    assert should_keep_tag("floral") is True
    assert should_keep_tag("a") is False
    assert should_keep_tag("123") is False
    assert should_keep_tag("files") is False
    assert should_keep_tag("amazing") is False

def test_extract_tags():
    # Test internal path: library/Animals/Animal (bear,cute) design.pes
    path = "library/Animals/Animal (bear,cute) design.pes"
    main, sub = extract_tags(path)
    assert "animals" in main
    assert "bear" in sub
    assert "cute" in sub
    
    # Test noise tag filtering
    path = "library/Floral/Floral (files,rose) Rose01.pes"
    main, sub = extract_tags(path)
    assert "floral" in main
    assert "rose" in sub
    assert "files" not in sub # should be filtered by should_keep_tag

def test_get_unique_target_path(tmp_path):
    target_dir = str(tmp_path / "Animals")
    os.makedirs(target_dir, exist_ok=True)
    
    main_tag = "Animal"
    sub_tags_str = "bear,cute"
    orig_name_clean = "design"
    orig_ext = ".pes"
    
    # No collision
    path, filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
    assert filename == "Animal (bear,cute) design.pes"
    
    # Create file to cause collision
    with open(path, 'w') as f: f.write("dummy")
    
    # Single collision
    path, filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
    assert filename == "Animal (bear,cute) design_1.pes"
    
    # Create another to cause second collision
    with open(path, 'w') as f: f.write("dummy")
    
    # Double collision
    path, filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
    assert filename == "Animal (bear,cute) design_2.pes"

def test_extract_tags_deep_path():
    # library/Animals/Mammals/Bears/Bear (brown) Kodiak.pes
    # Current implementation only takes the part directly after 'library' as main_tag
    path = "library/Animals/Mammals/Bears/Bear (brown) Kodiak.pes"
    main, sub = extract_tags(path)
    assert "animals" in main
    assert "brown" in sub
