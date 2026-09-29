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

    # 列表回傳 paginated envelope（id desc：較新嘅 d2 排前面）
    r = client.get("/dramas")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 24
    assert body["total_pages"] == 1
    assert [d["id"] for d in body["items"]] == [d2["id"], d1["id"]]
    # 無 episode 時 real_episode_count 預設 0
    assert all(d["real_episode_count"] == 0 for d in body["items"])

    # 分類篩選
    r = client.get("/dramas", params={"category_id": cat["id"]})
    body = r.json()
    assert body["total"] == 1
    assert [d["id"] for d in body["items"]] == [d1["id"]]

    # 搜尋
    r = client.get("/dramas", params={"search": "逆襲"})
    body = r.json()
    assert body["total"] == 1 and body["items"][0]["id"] == d1["id"]

    # 分頁：page=2&page_size=1，total 仍係 2、total_pages=2，本頁得較舊嗰部 d1
    r = client.get("/dramas", params={"page": 2, "page_size": 1})
    body = r.json()
    assert body["page"] == 2 and body["page_size"] == 1
    assert body["total"] == 2 and body["total_pages"] == 2
    assert [d["id"] for d in body["items"]] == [d1["id"]]

    # 詳情含 episodes（路徑唔受改動影響）
    r = client.get(f"/dramas/{d1['id']}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["episodes"] == []


def test_drama_list_source_filter(client, auth_headers):
    from app.database import SessionLocal
    from app.models.drama import Drama

    headers, _ = auth_headers()
    hongguo = _make_drama(client, headers, title="紅果劇")

    # CMS API 唔開 source 欄，直接落 DB 插一條 youku 劇
    db = SessionLocal()
    try:
        youku = Drama(title="優酷劇", source="youku", episode_count=24)
        db.add(youku)
        db.commit()
        youku_id = youku.id
    finally:
        db.close()

    # 唔帶 source：全部
    r = client.get("/dramas")
    assert r.json()["total"] == 2

    # source=hongguo
    r = client.get("/dramas", params={"source": "hongguo"})
    body = r.json()
    assert body["total"] == 1
    assert [d["id"] for d in body["items"]] == [hongguo["id"]]

    # source=youku
    r = client.get("/dramas", params={"source": "youku"})
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == youku_id

    # 唔存在嘅 source：空 envelope
    r = client.get("/dramas", params={"source": "no_such_source"})
    body = r.json()
    assert body["total"] == 0
    assert body["total_pages"] == 0
    assert body["items"] == []


def test_drama_list_real_episode_count(client, auth_headers):
    headers, _ = auth_headers()
    drama = _make_drama(client, headers, title="CMS 建劇")

    # metadata 設 episode_count=24（模擬優酷劇有 metadata 但未爬片）
    r = client.put(
        f"/cms/dramas/{drama['id']}", json={"episode_count": 24}, headers=headers
    )
    assert r.status_code == 200, r.text

    # list：episode_count=24 但 DB 真實集數 = 0
    r = client.get("/dramas")
    item = next(d for d in r.json()["items"] if d["id"] == drama["id"])
    assert item["episode_count"] == 24
    assert item["real_episode_count"] == 0

    # 建 3 集
    for n in (1, 2, 3):
        rr = client.post(
            "/cms/episodes",
            json={
                "drama_id": drama["id"],
                "episode_number": n,
                "title": f"第{n}集",
                "video_url": f"https://cdn.example.com/e{n}.mp4",
                "duration": 120,
            },
            headers=headers,
        )
        assert rr.status_code == 201, rr.text

    # list 應反映 grouped query 計出嘅真實 3 集
    r = client.get("/dramas")
    item = next(d for d in r.json()["items"] if d["id"] == drama["id"])
    assert item["real_episode_count"] == 3


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
