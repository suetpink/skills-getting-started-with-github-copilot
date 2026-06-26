import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_success(self, client):
        """
        Test successful retrieval of all activities.
        
        AAA Pattern:
        - Arrange: Create client
        - Act: Make GET request to /activities
        - Assert: Verify status 200 and 9 activities returned
        """
        # Arrange
        # Client is already provided by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert all(isinstance(name, str) for name in activities.keys())
        assert all(
            "description" in activity and 
            "schedule" in activity and 
            "max_participants" in activity and 
            "participants" in activity
            for activity in activities.values()
        )


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """
        Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Prepare valid activity name and email
        - Act: POST signup request
        - Assert: Verify status 200 and participant added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "student1@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "signed up" in response.json()["message"].lower()
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate(self, client):
        """
        Test signup attempt with duplicate email.
        
        AAA Pattern:
        - Arrange: Sign up email once, prepare for second attempt
        - Act: POST same email signup again
        - Assert: Verify status 400
        """
        # Arrange
        activity_name = "Programming Class"
        email = "student2@example.com"
        
        # First signup succeeds
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_activity_not_found(self, client):
        """
        Test signup with non-existent activity.
        
        AAA Pattern:
        - Arrange: Prepare fake activity name and valid email
        - Act: POST signup for non-existent activity
        - Assert: Verify status 404
        """
        # Arrange
        activity_name = "NonexistentActivity"
        email = "student3@example.com"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client):
        """
        Test successful unregister from an activity.
        
        AAA Pattern:
        - Arrange: Sign up email first
        - Act: DELETE unregister request
        - Assert: Verify status 200 and participant removed
        """
        # Arrange
        activity_name = "Gym Class"
        email = "student4@example.com"
        
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "unregistered" in response.json()["message"].lower()
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_not_enrolled(self, client):
        """
        Test unregister attempt for email not enrolled in activity.
        
        AAA Pattern:
        - Arrange: Use email never enrolled in activity
        - Act: DELETE unregister request
        - Assert: Verify status 400
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "student5@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_activity_not_found(self, client):
        """
        Test unregister from non-existent activity.
        
        AAA Pattern:
        - Arrange: Prepare fake activity name and valid email
        - Act: DELETE unregister from non-existent activity
        - Assert: Verify status 404
        """
        # Arrange
        activity_name = "NonexistentActivity"
        email = "student6@example.com"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRootRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirect(self, client):
        """
        Test root endpoint redirect to static files.
        
        AAA Pattern:
        - Arrange: Create client with follow_redirects=False
        - Act: GET request to root endpoint
        - Assert: Verify status 307 redirect
        """
        # Arrange
        client_no_redirect = TestClient(app, follow_redirects=False)
        
        # Act
        response = client_no_redirect.get("/")
        
        # Assert
        assert response.status_code == 307
        assert "location" in response.headers
