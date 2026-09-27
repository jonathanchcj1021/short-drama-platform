"""劇集公開路由 + 使用者劇集進度。"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, get_db
from app.models.drama import Drama
from app.models.episode import Episode
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.schemas.drama import DramaDetail, DramaOut
from app.schemas.progress import ProgressOut

router = APIRouter(prefix="/dramas", tags=["dramas"])


@router.get("", response_model=list[DramaOut])
def list_dramas(
    db: Session = Depends(get_db),
    category_id: int | None = Query(None),
    search: str | None = Query(None, description="標題關鍵字搜尋"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Drama).order_by(Drama.id.desc())
    if category_id is not None:
        stmt = stmt.where(Drama.category_id == category_id)
    if search:
        stmt = stmt.where(Drama.title.ilike(f"%{search}%"))
    stmt = stmt.offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{drama_id}", response_model=DramaDetail)
def get_drama(drama_id: int, db: Session = Depends(get_db)):
    drama = db.scalar(
        select(Drama).where(Drama.id == drama_id).options(selectinload(Drama.episodes))
    )
    if drama is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="劇集不存在")
    return drama


@router.get("/{drama_id}/progress", response_model=list[ProgressOut])
def get_drama_progress(
    drama_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    drama = db.get(Drama, drama_id)
    if drama is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="劇集不存在")

    stmt = (
        select(WatchProgress)
        .join(Episode, Episode.id == WatchProgress.episode_id)
        .where(WatchProgress.user_id == current_user.id, Episode.drama_id == drama_id)
    )
    return db.scalars(stmt).all()
