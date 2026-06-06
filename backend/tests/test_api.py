import pytest
from backend.database import File, Tag

def test_get_version(client):
    response = client.get("/api/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_get_files_empty(client):
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []

def test_toggle_star(client, db):
    # Create a dummy file
    test_file = File(name="test.pes", path="library/Test/test.pes", size=100)
    db.add(test_file)
    db.commit()
    
    # Toggle star ON
    response = client.post(f"/api/files/{test_file.id}/star")
    assert response.status_code == 200
    assert response.json()["is_starred"] is True
    
    # Toggle star OFF
    response = client.post(f"/api/files/{test_file.id}/star")
    assert response.status_code == 200
    assert response.json()["is_starred"] is False

def test_get_files_with_data(client, db):
    # Create a dummy file with tags
    tag_main = Tag(name="floral", is_main=True)
    tag_sub = Tag(name="rose", is_main=False)
    db.add_all([tag_main, tag_sub])
    db.commit()
    
    import datetime
    test_file = File(
        name="floral (rose) test.pes", 
        path="library/floral/floral (rose) test.pes", 
        size=1024,
        stitches=5000,
        modified_at=datetime.datetime.now()
    )
    test_file.tags = [tag_main, tag_sub]
    db.add(test_file)
    db.commit()
    
    # Test plain list
    response = client.get("/api/files")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "floral (rose) test.pes"
    assert data["items"][0]["main_tag"] == "floral"
    assert "rose" in data["items"][0]["sub_tags"]

    # Test tag filter
    response = client.get("/api/files?tag=floral")
    assert response.json()["total"] == 1
    
    response = client.get("/api/files?tag=rose")
    assert response.json()["total"] == 1
    
    response = client.get("/api/files?tag=nonexistent")
    assert response.json()["total"] == 0

def test_get_tags(client, db):
    tag_main = Tag(name="nature", is_main=True)
    tag_sub = Tag(name="leaf", is_main=False)
    db.add_all([tag_main, tag_sub])
    db.commit()
    
    # Tags only show up if they have files
    test_file = File(name="nature.pes", path="library/nature/nature.pes", size=100)
    test_file.tags = [tag_main, tag_sub]
    db.add(test_file)
    db.commit()
    
    response = client.get("/api/tags")
    assert response.status_code == 200
    data = response.json()
    assert any(t["name"] == "nature" for t in data["main"])
    assert any(t["name"] == "leaf" for t in data["sub"])
