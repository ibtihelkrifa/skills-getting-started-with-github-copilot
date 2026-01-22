"""Tests for activities endpoints"""
import pytest


def test_root_redirect(client):
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "Soccer Club" in data
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activities_has_required_fields(client):
    """Test that activities have all required fields"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_details in data.items():
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)


def test_signup_for_activity(client):
    """Test signing up a student for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_email(client):
    """Test that duplicate signups are rejected"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/Basketball Team/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        f"/activities/Basketball Team/signup?email={email}"
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_unregister_from_activity(client):
    """Test unregistering a student from an activity"""
    email = "unregister@mergington.edu"
    
    # First, sign up
    client.post(f"/activities/Soccer Club/signup?email={email}")
    
    # Then unregister
    response = client.post(
        f"/activities/Soccer Club/unregister?email={email}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert "Soccer Club" in data["message"]


def test_unregister_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404


def test_unregister_not_signed_up(client):
    """Test unregistering when not signed up"""
    response = client.post(
        "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_signup_and_verify_participant_list(client):
    """Test that signup adds participant to the list"""
    email = "verify@mergington.edu"
    
    # Sign up
    client.post(f"/activities/Art Workshop/signup?email={email}")
    
    # Get activities and verify participant is in list
    response = client.get("/activities")
    data = response.json()
    assert email in data["Art Workshop"]["participants"]


def test_unregister_and_verify_participant_list(client):
    """Test that unregister removes participant from the list"""
    email = "remove@mergington.edu"
    
    # Sign up
    client.post(f"/activities/Math Olympiad/signup?email={email}")
    
    # Verify participant is in list
    response = client.get("/activities")
    data = response.json()
    assert email in data["Math Olympiad"]["participants"]
    
    # Unregister
    client.post(f"/activities/Math Olympiad/unregister?email={email}")
    
    # Verify participant is removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data["Math Olympiad"]["participants"]


def test_predefined_participants_in_activities(client):
    """Test that predefined participants are present in activities"""
    response = client.get("/activities")
    data = response.json()
    
    # Check Chess Club has predefined participants
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    # Check Programming Class has predefined participants
    assert "emma@mergington.edu" in data["Programming Class"]["participants"]
    assert "sophia@mergington.edu" in data["Programming Class"]["participants"]
    
    # Check Gym Class has predefined participants
    assert "john@mergington.edu" in data["Gym Class"]["participants"]
    assert "olivia@mergington.edu" in data["Gym Class"]["participants"]
