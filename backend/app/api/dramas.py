"""劇集公開路由 + 使用者劇集進度。"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, get_db
from app.models.drama import Drama
from app.models.episode import Episode
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.schemas.drama import DramaDetail, DramaListEnvelope, DramaListItem
from app.schemas.progress import ProgressOut

router = APIRouter(prefix="/dramas", tags=["dramas"])


@router.get("", response_model=DramaListEnvelope)
def list_dramas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    category_id: int | None = Query(None),
    search: str | None = Query(None, description="標題關鍵字搜尋"),
    source: str | None = Query(None, description="來源平台精確篩選，例如 hongguo / youku"),
):
    filters = []
    if category_id is not None:
        filters.append(Drama.category_id == category_id)
    if search:
        filters.append(Drama.title.ilike(f"%{search}%"))
    if source is not None:
        filters.append(Drama.source == source)

    total = db.scalar(select(func.count()).select_from(Drama).where(*filters)) or 0
    total_pages = (total + page_size - 1) // page_size if page_size else 0

    stmt = (
        select(Drama)
        .where(*filters)
        .order_by(Drama.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    dramas = db.scalars(stmt).all()

    # 一條 grouped query 攞真實集數，避免 N+1
    count_map: dict[int, int] = {}
    if dramas:
        rows = db.execute(
            select(Episode.drama_id, func.count(Episode.id)).where(
                Episode.drama_id.in_([d.id for d in dramas])
            ).group_by(Episode.drama_id)
        ).all()
        count_map = {did: cnt for did, cnt in rows}

    items = []
    for drama in dramas:
        item = DramaListItem.model_validate(drama)
        item.real_episode_count = count_map.get(drama.id, 0)
        items.append(item)

    return DramaListEnvelope(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


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
