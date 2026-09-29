"""集數公開路由 + 播放 / 進度回報（需登入）。"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.billing import FREE_EPISODE_LIMIT, effective_is_vip
from app.core.deps import get_current_user, get_db
from app.core.security import TokenError, decode_token
from app.models.drama import Drama
from app.models.episode import Episode
from app.models.episode_unlock import EpisodeUnlock
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.schemas.episode import EpisodeOut
from app.schemas.progress import ProgressOut, ProgressReport
from app.services import hongguo_playback

router = APIRouter(prefix="/episodes", tags=["episodes"])


class StreamOut(BaseModel):
    episode: EpisodeOut
    video_url: str
    # 係咪有真片可播。False 時前端要顯示「敬請期待」占位，唔好黑畫面。
    available: bool = True
    # True = 呢集要睇 20 秒廣告先可以播（video_url 會係空字串）
    requires_ad: bool = False
    message: str | None = None


@router.get("/{episode_id}", response_model=EpisodeOut)
def get_episode(episode_id: int, db: Session = Depends(get_db)):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")
    return ep


def _resolve_upstream_url(
    ep: Episode, drama: Drama | None, db: Session
) -> str | None:
    """決定呢集實際要串流嘅上游片 URL。返 None = 冇片（敬請期待）。"""
    # 1) 純占位片（placeholder-soon.mp4，8KB 黑畫面）：冇真片。
    if ep.video_url and "placeholder-soon" in ep.video_url:
        return None

    source = drama.source if drama else None

    # 2) 紅果來源 + 有 player_path：開播時即時重抽新簽名 URL。
    if source == "hongguo" and ep.player_path:
        fresh = hongguo_playback.fetch_fresh_url(ep.player_path)
        if fresh and hongguo_playback.head_video_ok(fresh):
            if fresh != ep.video_url:
                ep.video_url = fresh
                db.commit()
                db.refresh(ep)
            return fresh
        # 重抽失敗：探現有 DB 嘅 video_url 仲生唔生。
        if hongguo_playback.head_video_ok(ep.video_url):
            return ep.video_url
        return None  # 舊 CDN 都過期：敬請期待

    # 3) 其他來源 / 本機 static：直接用 DB URL。
    return ep.video_url


def _has_stream_access(user: User, ep: Episode, drama: Drama | None, db: Session) -> bool:
    """決定用戶而家可不可以即時播呢集。

    規則：
    1. 劇唔存在 / 唔係收費劇 → 完全開放
    2. 有效 VIP → 全部任睇
    3. 集數 <= 頭 N 集 → 免費任睇
    4. EpisodeUnlock 有記錄（睇過廣告解鎖）→ 開放
    5. 否則要睇廣告
    """
    if drama is None or not drama.is_paid:
        return True
    if effective_is_vip(user):
        return True
    if ep.episode_number <= FREE_EPISODE_LIMIT:
        return True
    unlock = db.scalar(
        select(EpisodeUnlock).where(
            EpisodeUnlock.user_id == user.id,
            EpisodeUnlock.episode_id == ep.id,
        )
    )
    return unlock is not None


@router.get("/{episode_id}/stream", response_model=StreamOut)
def stream_episode(
    episode_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")

    drama = db.get(Drama, ep.drama_id)
    upstream = _resolve_upstream_url(ep, drama, db)
    if upstream is None:
        return StreamOut(episode=ep, video_url="", available=False, message="此集敬請期待")

    # 免費用戶未解鎖嘅集：要睇廣告
    if not _has_stream_access(current_user, ep, drama, db):
        return StreamOut(
            episode=ep,
            video_url="",
            available=True,
            requires_ad=True,
            message="免費用戶可免費觀看頭10集，之後需觀看廣告解鎖",
        )

    # 紅果 CDN 有 Referer 防盗鏈（外站 Referer 返 403），所以片經我哋後端代理：
    # 前端只係 request 我哋呢個 domain，唔會帶出 github.io 嘅 Referer。
    auth = request.headers.get("authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    base = str(request.base_url).rstrip("/")
    media_url = f"{base}/episodes/{ep.id}/media"
    if token:
        media_url += f"?token={token}"
    return StreamOut(episode=ep, video_url=media_url, available=True)


def _authorize_media(token: str | None, db: Session) -> User:
    """媒體代理用 query token 驗證（<video> tag 帶唔到 Authorization header）。"""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未認證")
    try:
        payload = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="使用者不存在")
    return user


@router.api_route("/{episode_id}/media", methods=["GET", "HEAD"])
def media_proxy(
    episode_id: int,
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = _authorize_media(token, db)
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")
    drama = db.get(Drama, ep.drama_id)

    # 同 stream endpoint 一樣嘅閘，防止用戶直接打 media URL 繞過廣告
    if not _has_stream_access(user, ep, drama, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此集需觀看廣告解鎖",
        )

    upstream = _resolve_upstream_url(ep, drama, db)
    if upstream is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="此集敬請期待")

    # 轉發 Range request，串流畀前端。
    headers = {}
    rng = request.headers.get("range")
    if rng:
        headers["Range"] = rng
    client = httpx.Client(
        timeout=30.0, follow_redirects=True, headers={"User-Agent": hongguo_playback.UA}
    )
    up_ctx = client.stream("GET", upstream, headers=headers)
    up = up_ctx.__enter__()
    try:
        up.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        up_ctx.__exit__(None, None, None)
        client.close()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="片源暫時唔得"
        ) from exc

    resp_headers = {
        "Content-Type": up.headers.get("content-type", "video/mp4"),
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-store",
    }
    clen = up.headers.get("content-length")
    if clen:
        resp_headers["Content-Length"] = clen
    crange = up.headers.get("content-range")
    if crange:
        resp_headers["Content-Range"] = crange
    up_status = up.status_code

    def gen():
        try:
            for chunk in up.iter_bytes(chunk_size=64 * 1024):
                yield chunk
        finally:
            up_ctx.__exit__(None, None, None)
            client.close()

    return StreamingResponse(gen(), status_code=up_status, headers=resp_headers)


@router.post("/{episode_id}/unlock")
def unlock_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """睇完 20 秒廣告之後 call 呢個 endpoint 解鎖呢集。Idempotent。"""
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")

    existing = db.scalar(
        select(EpisodeUnlock).where(
            EpisodeUnlock.user_id == current_user.id,
            EpisodeUnlock.episode_id == episode_id,
        )
    )
    if existing is None:
        db.add(EpisodeUnlock(user_id=current_user.id, episode_id=episode_id))
        db.commit()

    return {"episode_id": episode_id, "unlocked": True}


@router.post("/{episode_id}/progress", response_model=ProgressOut)
def report_progress(
    episode_id: int,
    body: ProgressReport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")

    progress = db.scalar(
        select(WatchProgress).where(
            WatchProgress.user_id == current_user.id,
            WatchProgress.episode_id == episode_id,
        )
    )
    if progress is None:
        progress = WatchProgress(user_id=current_user.id, episode_id=episode_id)
        db.add(progress)

    progress.current_time = body.current_time
    if body.duration is not None:
        progress.duration = body.duration
    progress.completed = body.completed
    db.commit()
    db.refresh(progress)

    return ProgressOut(
        episode_id=progress.episode_id,
        current_time=progress.current_time,
        duration=progress.duration,
        completed=progress.completed,
        updated_at=progress.updated_at,
    )
