"""
Test suite for Mergington High School Activity Management API

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and TestClient
- Act: Call the API endpoint
- Assert: Verify the response status and data
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Practice team play, drills, and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["natalie@mergington.edu", "ryan@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming technique and endurance in the pool",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 4:00 PM",
            "max_participants": 16,
            "participants": ["mason@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Workshop": {
            "description": "Develop acting skills, improv, and stage production",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "alex@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build robots, solve engineering challenges, and compete",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "chloe@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions with problem solving practice",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["logan@mergington.edu", "zoe@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test completes
    activities.clear()
    activities.update(original_activities)


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestGetActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: No setup needed
        Act: Send GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify we get all 9 activities
        assert len(data) == 9
        
        # Verify activity structure
        assert "Chess Club" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert "schedule" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_succeeds(self, client, reset_activities):
        """
        Arrange: Prepare a valid activity and new email
        Act: Send POST request to sign up new student
        Assert: Signup succeeds with 200 status and confirmation message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was added to participants
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()["Chess Club"]
        assert email in updated_activity["participants"]


class TestUnregisterParticipant:
    """Test DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_unregister_existing_participant_succeeds(self, client, reset_activities):
        """
        Arrange: Prepare an activity with existing participant
        Act: Send DELETE request to unregister participant
        Assert: Unregistration succeeds with 200 status and confirmation message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club participants
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was removed from participants
        activities_response = client.get("/activities")
        updated_activity = activities_response.json()["Chess Club"]
        assert email not in updated_activity["participants"]


# ============================================================================
# ERROR SCENARIO TESTS
# ============================================================================

class TestSignupErrorScenarios:
    """Test error handling for signup endpoint"""
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        Arrange: Attempt to sign up with email already registered in activity
        Act: Send POST request with duplicate email
        Assert: Returns 400 Bad Request with error detail
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_invalid_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Attempt to sign up for non-existent activity
        Act: Send POST request with invalid activity name
        Assert: Returns 404 Not Found with error detail
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestUnregisterErrorScenarios:
    """Test error handling for unregister endpoint"""
    
    def test_unregister_invalid_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Attempt to unregister from non-existent activity
        Act: Send DELETE request with invalid activity name
        Assert: Returns 404 Not Found with error detail
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_participant_not_in_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Attempt to unregister student not in activity
        Act: Send DELETE request for participant not in participants list
        Assert: Returns 404 Not Found with error detail
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notamember@mergington.edu"  # Not in Chess Club
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
