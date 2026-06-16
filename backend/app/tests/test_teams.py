"""Tests for team participants and their rosters."""

from app.tests.conftest import register_and_login


def make_tournament(client, headers, name="Team Cup"):
    return client.post(
        "/tournaments",
        json={"name": name, "format": "SINGLE_ELIM"},
        headers=headers,
    ).json()


def add_team(client, headers, tid, name="Red"):
    return client.post(
        f"/tournaments/{tid}/participants",
        json={"name": name, "type": "TEAM"},
        headers=headers,
    ).json()


def add_member(client, headers, tid, pid, name):
    return client.post(
        f"/tournaments/{tid}/participants/{pid}/members",
        json={"name": name},
        headers=headers,
    )


def test_add_members_to_team(client, auth_headers):
    t = make_tournament(client, auth_headers)
    team = add_team(client, auth_headers, t["id"])
    assert team["type"] == "TEAM"
    assert team["members"] == []

    add_member(client, auth_headers, t["id"], team["id"], "Ana")
    add_member(client, auth_headers, t["id"], team["id"], "Bo")

    participants = client.get(f"/tournaments/{t['id']}/participants").json()
    members = participants[0]["members"]
    assert [m["name"] for m in members] == ["Ana", "Bo"]


def test_rename_member(client, auth_headers):
    t = make_tournament(client, auth_headers)
    team = add_team(client, auth_headers, t["id"])
    m = add_member(client, auth_headers, t["id"], team["id"], "Ana").json()

    r = client.patch(
        f"/tournaments/{t['id']}/participants/{team['id']}/members/{m['id']}",
        json={"name": "Ana B."},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Ana B."


def test_delete_member(client, auth_headers):
    t = make_tournament(client, auth_headers)
    team = add_team(client, auth_headers, t["id"])
    m = add_member(client, auth_headers, t["id"], team["id"], "Ana").json()

    r = client.delete(
        f"/tournaments/{t['id']}/participants/{team['id']}/members/{m['id']}",
        headers=auth_headers,
    )
    assert r.status_code == 204
    participants = client.get(f"/tournaments/{t['id']}/participants").json()
    assert participants[0]["members"] == []


def test_cannot_add_member_to_non_team(client, auth_headers):
    t = make_tournament(client, auth_headers)
    player = client.post(
        f"/tournaments/{t['id']}/participants",
        json={"name": "Solo"},
        headers=auth_headers,
    ).json()
    r = add_member(client, auth_headers, t["id"], player["id"], "Ana")
    assert r.status_code == 400


def test_cannot_edit_roster_after_generate(client, auth_headers):
    t = make_tournament(client, auth_headers)
    a = add_team(client, auth_headers, t["id"], "Red")
    add_team(client, auth_headers, t["id"], "Blue")
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)

    r = add_member(client, auth_headers, t["id"], a["id"], "Ana")
    assert r.status_code == 400


def test_non_owner_cannot_edit_roster(client, auth_headers):
    t = make_tournament(client, auth_headers)
    team = add_team(client, auth_headers, t["id"])
    intruder = register_and_login(client, email="intruder@example.com")
    r = add_member(client, intruder, t["id"], team["id"], "Ana")
    assert r.status_code == 403


def test_deleting_team_removes_members(client, auth_headers):
    t = make_tournament(client, auth_headers)
    team = add_team(client, auth_headers, t["id"])
    add_member(client, auth_headers, t["id"], team["id"], "Ana")

    r = client.delete(
        f"/tournaments/{t['id']}/participants/{team['id']}", headers=auth_headers
    )
    assert r.status_code == 204
    assert client.get(f"/tournaments/{t['id']}/participants").json() == []


def test_deleting_tournament_with_teams(client, auth_headers):
    t = make_tournament(client, auth_headers)
    team = add_team(client, auth_headers, t["id"])
    add_member(client, auth_headers, t["id"], team["id"], "Ana")

    r = client.delete(f"/tournaments/{t['id']}", headers=auth_headers)
    assert r.status_code == 204
    assert client.get(f"/tournaments/{t['id']}").status_code == 404
