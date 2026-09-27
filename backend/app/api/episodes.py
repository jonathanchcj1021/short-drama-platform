"""集數公開路由 + 播放 / 進度回報（需登入）。"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.episode import Episode
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.schemas.episode import EpisodeOut
from app.schemas.progress import ProgressOut, ProgressReport

router = APIRouter(prefix="/episodes", tags=["episodes"])


class StreamOut(BaseModel):
    episode: EpisodeOut
    video_url: str


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
    return StreamOut(episode=ep, video_url=ep.video_url)


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
