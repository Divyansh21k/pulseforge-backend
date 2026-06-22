def _setup_team_and_project(client, organizer_headers, org="VIT University"):
    p1 = client.post("/api/participants/", json={"full_name": "P One", "email": "p1@x.com", "organization": org}, headers=organizer_headers).json()
    p2 = client.post("/api/participants/", json={"full_name": "P Two", "email": "p2@x.com", "organization": org}, headers=organizer_headers).json()
    team = client.post("/api/teams/", json={"name": "Team X", "member_ids": [p1["id"], p2["id"]]}, headers=organizer_headers).json()
    project = client.post(
        "/api/projects/",
        json={"team_id": team["id"], "title": "Proj", "description": "a project", "tech_stack_text": "python, react"},
        headers=organizer_headers,
    ).json()
    return team, project


def test_reviewer_with_same_org_excluded_from_assignment(client, organizer_headers):
    team, project = _setup_team_and_project(client, organizer_headers, org="VIT University")

    conflicted = client.post(
        "/api/reviewers/",
        json={"full_name": "Conflicted Rev", "email": "conf@x.com", "organization": "VIT University", "expertise_text": "python"},
        headers=organizer_headers,
    ).json()
    clean = client.post(
        "/api/reviewers/",
        json={"full_name": "Clean Rev", "email": "clean@x.com", "organization": "MIT", "expertise_text": "python, react"},
        headers=organizer_headers,
    ).json()

    r = client.post("/api/reviewers/assign", json={"reviewers_per_project": 2}, headers=organizer_headers)
    assert r.status_code == 200
    assignments = r.json()["assignments"]

    assigned_reviewer_ids = {a["reviewer_id"] for a in assignments if a["project_id"] == project["id"]}
    assert conflicted["id"] not in assigned_reviewer_ids
    assert clean["id"] in assigned_reviewer_ids


def test_assignment_fails_gracefully_with_no_reviewers(client, organizer_headers):
    _setup_team_and_project(client, organizer_headers)
    r = client.post("/api/reviewers/assign", json={"reviewers_per_project": 1}, headers=organizer_headers)
    assert r.status_code == 400


def test_assignment_score_breakdown_present(client, organizer_headers):
    team, project = _setup_team_and_project(client, organizer_headers, org="Org A")
    client.post(
        "/api/reviewers/",
        json={"full_name": "Rev", "email": "rev@x.com", "organization": "Org B", "expertise_text": "python, react"},
        headers=organizer_headers,
    )
    r = client.post("/api/reviewers/assign", json={"reviewers_per_project": 1}, headers=organizer_headers)
    assert r.status_code == 200
    a = r.json()["assignments"][0]
    for key in ["expertise_score", "workload_score", "conflict_score", "diversity_score", "total_score"]:
        assert key in a
