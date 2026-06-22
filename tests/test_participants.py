def test_register_participant(client, organizer_headers):
    r = client.post(
        "/api/participants/",
        json={"full_name": "Alice Kumar", "email": "alice@test.com", "organization": "VIT"},
        headers=organizer_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "alice@test.com"
    assert "id" in body


def test_duplicate_email_rejected(client, organizer_headers):
    payload = {"full_name": "Alice Kumar", "email": "alice@test.com", "organization": "VIT"}
    r1 = client.post("/api/participants/", json=payload, headers=organizer_headers)
    assert r1.status_code == 201

    r2 = client.post("/api/participants/", json=payload, headers=organizer_headers)
    assert r2.status_code == 409


def test_fuzzy_name_duplicate_detected(client, organizer_headers):
    client.post("/api/participants/", json={"full_name": "Alice Kumar", "email": "a1@test.com", "organization": "VIT"}, headers=organizer_headers)
    r2 = client.post("/api/participants/", json={"full_name": "Alicia Kumar", "email": "a2@test.com", "organization": "VIT"}, headers=organizer_headers)
    target_id = r2.json()["id"]

    r = client.post(f"/api/duplicates/check/{target_id}", headers=organizer_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["matches_found"] >= 1
    assert body["matches"][0]["match_type"] == "fuzzy_name"


def test_distinct_participants_not_flagged(client, organizer_headers):
    client.post("/api/participants/", json={"full_name": "Bob Singh", "email": "bob@test.com", "organization": "MIT"}, headers=organizer_headers)
    r2 = client.post("/api/participants/", json={"full_name": "Carla Diaz", "email": "carla@test.com", "organization": "Stanford"}, headers=organizer_headers)
    target_id = r2.json()["id"]

    r = client.post(f"/api/duplicates/check/{target_id}", headers=organizer_headers)
    assert r.status_code == 200
    assert r.json()["matches_found"] == 0


def test_participant_not_found_404(client, organizer_headers):
    r = client.get("/api/participants/9999", headers=organizer_headers)
    assert r.status_code == 404
