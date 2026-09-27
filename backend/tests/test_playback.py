"""播放 / 觀看進度測試。"""


def _setup_drama_with_episode(client, headers):
    drama = client.post(
        "/cms/dramas",
        json={"title": "播放測試劇"},
        headers=headers,
    ).json()
    ep = client.post(
        "/cms/episodes",
        json={
            "drama_id": drama["id"],
            "episode_number": 1,
            "title": "E01",
            "video_url": "https://cdn.example.com/e1.mp4",
            "duration": 100,
        },
        headers=headers,
    ).json()
    return drama, ep


def test_stream_requires_login(client, auth_headers):
    headers, _ = auth_headers()
    drama, ep = _setup_drama_with_episode(client, headers)

    # 未授權
    r = client.get(f"/episodes/{ep['id']}/stream")
    assert r.status_code == 401

    # 已登入可取得播放位址
    r = client.get(f"/episodes/{ep['id']}/stream", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["video_url"] == "https://cdn.example.com/e1.mp4"
    assert body["episode"]["id"] == ep["id"]


def test_progress_report_and_fetch(client, auth_headers):
    headers, _ = auth_headers()
    drama, ep = _setup_drama_with_episode(client, headers)

    # 回報進度（未授權應拒絕）
    r = client.post(f"/episodes/{ep['id']}/progress", json={"current_time": 30, "completed": False})
    assert r.status_code == 401

    # 已登入回報
    r = client.post(
        f"/episodes/{ep['id']}/progress",
        json={"current_time": 30, "duration": 100, "completed": False},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["current_time"] == 30

    # 更新進度（同一筆 upsert）
    r = client.post(
        f"/episodes/{ep['id']}/progress",
        json={"current_time": 99, "completed": True},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["current_time"] == 99
    assert r.json()["completed"] is True

    # 取得該劇的觀看進度
    r = client.get(f"/dramas/{drama['id']}/progress", headers=headers)
    assert r.status_code == 200
    prog = r.json()
    assert len(prog) == 1
    assert prog[0]["episode_id"] == ep["id"]
    assert prog[0]["current_time"] == 99
    assert prog[0]["completed"] is True
