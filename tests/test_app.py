import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store the original state
    original_state = deepcopy(activities)
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original_state)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_success(self, client, reset_activities):
        # Arrange: No setup needed, activities already populated

        # Act: Make GET request
        response = client.get("/activities")

        # Assert: Verify status code and response structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, client, reset_activities):
        # Arrange: No setup needed

        # Act: Make GET request
        response = client.get("/activities")
        data = response.json()

        # Assert: Verify activity structure
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client, reset_activities):
        # Arrange: Clear participants from Chess Club for this test
        activity_name = "Chess Club"
        test_email = "newuser@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act: Sign up new participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Verify signup succeeded
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_participant_rejected(self, client, reset_activities):
        # Arrange: Get existing participant
        activity_name = "Chess Club"
        existing_email = activities[activity_name]["participants"][0]

        # Act: Try to sign up with duplicate email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert: Verify duplicate is rejected
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange: Use non-existent activity
        activity_name = "Nonexistent Club"
        test_email = "student@mergington.edu"

        # Act: Try to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_participant_success(self, client, reset_activities):
        # Arrange: Get existing participant
        activity_name = "Chess Club"
        participant_email = activities[activity_name]["participants"][0]
        initial_count = len(activities[activity_name]["participants"])

        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": participant_email}
        )

        # Assert: Verify participant was removed
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert participant_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        # Arrange: Use email not in activity
        activity_name = "Chess Club"
        nonexistent_email = "notinlist@mergington.edu"

        # Act: Try to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": nonexistent_email}
        )

        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange: Use non-existent activity
        activity_name = "Nonexistent Club"
        test_email = "student@mergington.edu"

        # Act: Try to remove from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": test_email}
        )

        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
