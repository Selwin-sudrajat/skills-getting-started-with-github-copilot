from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert len(data) == 15

    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_successfully_adds_student(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_signup(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_400_when_activity_is_full(client):
    activity_name = "Debate Team"
    max_participants = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])

    for idx in range(max_participants - current_count):
        email = f"fill{idx}@mergington.edu"
        fill_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        assert fill_response.status_code == 200

    overflow_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overflow@mergington.edu"},
    )

    assert overflow_response.status_code == 400
    assert overflow_response.json()["detail"] == "Activity is full"


def test_signup_returns_400_for_invalid_email(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "not-an-email"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email format"


def test_unregister_successfully_removes_student(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_non_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "notenrolled@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
