def _setup_project_and_reviewers(client, organizer_headers):
    p1 = client.post("/api/participants/", json={"full_name": "A", "email": "a@x.com", "organization": "Org A"}, headers=organizer_headers).json()
    team = client.post("/api/teams/", json={"name": "Team", "member_ids": [p1["id"]]}, headers=organizer_headers).json()
    project = client.post(
        "/api/projects/", json={"team_id": team["id"], "title": "P", "description": "d"},
        headers=organizer_headers,
    ).json()
    rev1 = client.post("/api/reviewers/", json={"full_name": "R1", "email": "r1@x.com"}, headers=organizer_headers).json()
    rev2 = client.post("/api/reviewers/", json={"full_name": "R2", "email": "r2@x.com"}, headers=organizer_headers).json()
    return project, rev1, rev2


def test_submit_evaluation_computes_weighted_raw_score(client, organizer_headers):
    project, rev1, _ = _setup_project_and_reviewers(client, organizer_headers)
    r = client.post(
        "/api/evaluations/",
        json={
            "project_id": project["id"], "reviewer_id": rev1["id"],
            "innovation_score": 10, "technical_score": 10, "impact_score": 10, "presentation_score": 10,
        },
        headers=organizer_headers,
    )
    assert r.status_code == 201
    assert r.json()["raw_score"] == 10.0


def test_normalize_handles_lenient_and_harsh_reviewers(client, organizer_headers):
    project, rev1, rev2 = _setup_project_and_reviewers(client, organizer_headers)
    client.post("/api/evaluations/", json={
        "project_id": project["id"], "reviewer_id": rev1["id"],
        "innovation_score": 9, "technical_score": 9, "impact_score": 9, "presentation_score": 9,
    }, headers=organizer_headers)
    client.post("/api/evaluations/", json={
        "project_id": project["id"], "reviewer_id": rev2["id"],
        "innovation_score": 5, "technical_score": 5, "impact_score": 5, "presentation_score": 5,
    }, headers=organizer_headers)

    r = client.post("/api/evaluations/normalize", headers=organizer_headers)
    assert r.status_code == 200
    assert r.json()["evaluations_normalized"] == 2

    evals = client.get(f"/api/evaluations/project/{project['id']}", headers=organizer_headers).json()
    assert all(e["normalized_score"] is not None for e in evals)


def test_bias_scan_runs_without_error_on_small_dataset(client, organizer_headers):
    project, rev1, rev2 = _setup_project_and_reviewers(client, organizer_headers)
    client.post("/api/evaluations/", json={
        "project_id": project["id"], "reviewer_id": rev1["id"],
        "innovation_score": 8, "technical_score": 8, "impact_score": 8, "presentation_score": 8,
    }, headers=organizer_headers)
    client.post("/api/evaluations/normalize", headers=organizer_headers)

    r = client.post("/api/evaluations/bias-scan", headers=organizer_headers)
    assert r.status_code == 200
    assert "total_flags" in r.json()


def test_evaluation_for_missing_project_404s(client, organizer_headers):
    rev1 = client.post("/api/reviewers/", json={"full_name": "R", "email": "r@x.com"}, headers=organizer_headers).json()
    r = client.post("/api/evaluations/", json={
        "project_id": 9999, "reviewer_id": rev1["id"],
        "innovation_score": 5, "technical_score": 5, "impact_score": 5, "presentation_score": 5,
    }, headers=organizer_headers)
    assert r.status_code == 404


def test_score_bounds_enforced(client, organizer_headers):
    project, rev1, _ = _setup_project_and_reviewers(client, organizer_headers)
    r = client.post("/api/evaluations/", json={
        "project_id": project["id"], "reviewer_id": rev1["id"],
        "innovation_score": 15, "technical_score": 5, "impact_score": 5, "presentation_score": 5,
    }, headers=organizer_headers)
    assert r.status_code == 422
