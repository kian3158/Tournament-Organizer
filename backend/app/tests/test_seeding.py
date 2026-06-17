"""Tests for manual seed reordering."""

from app.tests.conftest import register_and_login
from app.tests.test_editing import make


def seeds(client, tid):
    return {
        p["id"]: p["seed"]
        for p in client.get(f"/tournaments/{tid}/participants").json()
    }


def test_reorder_sets_seeds_by_position(client, auth_headers):
    t, ids = make(client, auth_headers, players=3)
    new_order = [ids[2], ids[0], ids[1]]
    r = client.put(
        f"/tournaments/{t['id']}/participants/order",
        json={"participant_ids": new_order},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    s = seeds(client, t["id"])
    assert s[ids[2]] == 1 and s[ids[0]] == 2 and s[ids[1]] == 3


def test_reorder_rejects_incomplete_list(client, auth_headers):
    t, ids = make(client, auth_headers, players=3)
    r = client.put(
        f"/tournaments/{t['id']}/participants/order",
        json={"participant_ids": ids[:2]},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_reorder_rejected_after_generate(client, auth_headers):
    t, ids = make(client, auth_headers, players=4)
    client.post(f"/tournaments/{t['id']}/generate", headers=auth_headers)
    r = client.put(
        f"/tournaments/{t['id']}/participants/order",
        json={"participant_ids": list(reversed(ids))},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_reorder_non_owner_forbidden(client, auth_headers):
    t, ids = make(client, auth_headers, players=3)
    intruder = register_and_login(client, email="seedintruder@example.com")
    r = client.put(
        f"/tournaments/{t['id']}/participants/order",
        json={"participant_ids": ids},
        headers=intruder,
    )
    assert r.status_code == 403
