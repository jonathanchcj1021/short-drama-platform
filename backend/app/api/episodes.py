"""集數公開路由 + 播放 / 進度回報（需登入）。"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.drama import Drama
from app.models.episode import Episode
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
    message: str | None = None


@router.get("/{episode_id}", response_model=EpisodeOut)
def get_episode(episode_id: int, db: Session = Depends(get_db)):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")
    return ep


@router.get("/{episode_id}/stream", response_model=StreamOut)
def stream_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")

    # 1) 純占位片（placeholder-soon.mp4，8KB 黑畫面）：優雅返「冇片」狀態，
    #    等前端顯示「敬請期待」海報，唔好黑畫面。
    if ep.video_url and "placeholder-soon" in ep.video_url:
        return StreamOut(
            episode=ep, video_url="", available=False, message="此集敬請期待"
        )

    drama = db.get(Drama, ep.drama_id)
    source = drama.source if drama else None

    # 紅果來源 + 有 player_path：開播時即時重抓新簽名 URL，唔長存過期 CDN URL。
    if source == "hongguo" and ep.player_path:
        fresh = hongguo_playback.fetch_fresh_url(ep.player_path)
        if fresh and hongguo_playback.head_video_ok(fresh):
            # 新 URL 合格：順手寫回 DB 做 cache，再返畀前端。
            if fresh != ep.video_url:
                ep.video_url = fresh
                db.commit()
                db.refresh(ep)
            return StreamOut(episode=ep, video_url=fresh, available=True)

        # 重抓失敗 / 新 URL 唔合格：探現有 DB 嘅 video_url 仲生唔生。
        if hongguo_playback.head_video_ok(ep.video_url):
            return StreamOut(episode=ep, video_url=ep.video_url, available=True)

        # 舊 CDN URL 都過期（403 等）：拎唔到新片，優雅顯示「敬請期待」，
        # 唔好再返黑畫面占位片。
        return StreamOut(
            episode=ep,
            video_url="",
            available=False,
            message="此集敬請期待",
        )

    # 其他來源（或紅果但冇 player_path）：照舊返 DB 嘅 video_url。
    return StreamOut(episode=ep, video_url=ep.video_url, available=True)


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
