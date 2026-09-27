"""劇集 / 分類 / 集數 CRUD 測試。"""


def _make_category(client, headers, slug="romance", name="Romance"):
    r = client.post(
        "/cms/categories",
        json={"name": name, "slug": slug, "description": "浪漫短劇"},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


def _make_drama(client, headers, title="首戰王妃", category_id=None):
    r = client.post(
        "/cms/dramas",
        json={"title": title, "description": "一場宮鬥", "category_id": category_id},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_cms_requires_auth(client):
    r = client.post("/cms/categories", json={"name": "x", "slug": "x"})
    assert r.status_code == 401


def test_category_crud(client, auth_headers):
    headers, _ = auth_headers()
    cat = _make_category(client, headers)

    # 列表公開可讀
    r = client.get("/categories")
    assert r.status_code == 200
    assert any(c["id"] == cat["id"] for c in r.json())

    # 更新
    r = client.put(f"/cms/categories/{cat['id']}", json={"name": "新分類"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "新分類"

    # 刪除
    r = client.delete(f"/cms/categories/{cat['id']}", headers=headers)
    assert r.status_code == 204
    assert client.get(f"/categories/{cat['id']}").status_code == 404


def test_drama_list_filter_search_and_detail(client, auth_headers):
    headers, _ = auth_headers()
    cat = _make_category(client, headers, slug="crime", name="Crime")

    d1 = _make_drama(client, headers, title="逆襲人生", category_id=cat["id"])
    d2 = _make_drama(client, headers, title="總裁的替身嬌妻", category_id=None)

    # 列表
    r = client.get("/dramas")
    assert r.status_code == 200
    assert len(r.json()) == 2

    # 分類篩選
    r = client.get("/dramas", params={"category_id": cat["id"]})
    assert [d["id"] for d in r.json()] == [d1["id"]]

    # 搜尋
    r = client.get("/dramas", params={"search": "逆襲"})
    assert len(r.json()) == 1 and r.json()[0]["id"] == d1["id"]

    # 分頁
    r = client.get("/dramas", params={"skip": 1, "limit": 1})
    assert len(r.json()) == 1

    # 詳情含 episodes
    r = client.get(f"/dramas/{d1['id']}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["episodes"] == []


def test_episode_crud_appears_in_drama_detail(client, auth_headers):
    headers, _ = auth_headers()
    drama = _make_drama(client, headers, title="含集數劇")

    r = client.post(
        "/cms/episodes",
        json={
            "drama_id": drama["id"],
            "episode_number": 1,
            "title": "第一集",
            "video_url": "https://cdn.example.com/e1.mp4",
            "duration": 120,
        },
        headers=headers,
    )
    assert r.status_code == 201, r.text
    ep = r.json()

    # 劇集詳情應含此集
    detail = client.get(f"/dramas/{drama['id']}").json()
    assert len(detail["episodes"]) == 1
    assert detail["episodes"][0]["title"] == "第一集"

    # 更新集數
    r = client.put(f"/cms/episodes/{ep['id']}", json={"title": "第一集（修正）"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "第一集（修正）"

    # 刪除
    r = client.delete(f"/cms/episodes/{ep['id']}", headers=headers)
    assert r.status_code == 204
    assert client.get(f"/episodes/{ep['id']}").status_code == 404
