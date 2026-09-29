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
from app.services import hongguo_refresh

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

    placeholder = "此集敬請期待"

    # 1) 占位片（placeholder-soon.mp4）：優雅返「冇片」狀態，等前端顯示海報。
    if hongguo_refresh.is_placeholder_url(ep.video_url):
        return StreamOut(
            episode=ep, video_url="", available=False, message=placeholder
        )

    # 2) 本機 static mp4 / 其他非紅果 URL：原價返。
    if not hongguo_refresh.is_hongguo_signed_url(ep.video_url):
        return StreamOut(episode=ep, video_url=ep.video_url, available=True)

    # 3) 紅果 signed URL：探活；死咗就即時重簽。
    drama = db.get(Drama, ep.drama_id)
    series_id = drama.hongguo_series_id if drama else None
    new_url, used_path = hongguo_refresh.resolve_hongguo_url(
        episode_id=ep.id,
        drama_series_id=series_id,
        episode_number=ep.episode_number,
        stored_player_path=ep.player_path,
        old_url=ep.video_url,
    )

    if not new_url:
        # 拎唔到新片（冇 mapping / 紅果抽唔到）：優雅顯示「敬請期待」。
        return StreamOut(
            episode=ep, video_url="", available=False, message=placeholder
        )

    # 順手將新 URL + player_path 寫回 DB。
    changed = False
    if new_url != ep.video_url:
        ep.video_url = new_url
        changed = True
    if used_path and used_path != ep.player_path:
        ep.player_path = used_path
        changed = True
    if changed:
        db.commit()
        db.refresh(ep)

    return StreamOut(episode=ep, video_url=new_url, available=True)


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
