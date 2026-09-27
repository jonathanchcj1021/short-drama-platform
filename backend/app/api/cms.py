"""CMS 路由：寫操作（需管理員權限）。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_db, require_admin
from app.models.category import Category
from app.models.drama import Drama
from app.models.episode import Episode
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.drama import DramaCreate, DramaOut, DramaUpdate
from app.schemas.episode import EpisodeCreate, EpisodeOut, EpisodeUpdate

router = APIRouter(prefix="/cms", tags=["cms"], dependencies=[Depends(require_admin)])


# ---------- Dramas（管理用完整列表，上限 1000） ----------
@router.get("/dramas", response_model=list[DramaOut])
def list_cms_dramas(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 1000,
):
    stmt = (
        select(Drama)
        .options(selectinload(Drama.category))
        .order_by(Drama.id.desc())
        .offset(skip)
        .limit(min(limit, 1000))
    )
    return db.scalars(stmt).all()


# ---------- Categories ----------
@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    cat = Category(**body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分類不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分類不存在")
    db.delete(cat)
    db.commit()


# ---------- Dramas ----------
@router.post("/dramas", response_model=DramaOut, status_code=status.HTTP_201_CREATED)
def create_drama(body: DramaCreate, db: Session = Depends(get_db)):
    drama = Drama(**body.model_dump())
    db.add(drama)
    db.commit()
    db.refresh(drama)
    return drama


@router.put("/dramas/{drama_id}", response_model=DramaOut)
def update_drama(drama_id: int, body: DramaUpdate, db: Session = Depends(get_db)):
    drama = db.get(Drama, drama_id)
    if drama is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="劇集不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(drama, k, v)
    db.commit()
    db.refresh(drama)
    return drama


@router.delete("/dramas/{drama_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_drama(drama_id: int, db: Session = Depends(get_db)):
    drama = db.get(Drama, drama_id)
    if drama is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="劇集不存在")
    db.delete(drama)
    db.commit()


# ---------- Episodes ----------
@router.post("/episodes", response_model=EpisodeOut, status_code=status.HTTP_201_CREATED)
def create_episode(body: EpisodeCreate, db: Session = Depends(get_db)):
    drama = db.get(Drama, body.drama_id)
    if drama is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="所屬劇集不存在")
    ep = Episode(**body.model_dump())
    db.add(ep)
    db.commit()
    db.refresh(ep)
    return ep


@router.put("/episodes/{episode_id}", response_model=EpisodeOut)
def update_episode(episode_id: int, body: EpisodeUpdate, db: Session = Depends(get_db)):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(ep, k, v)
    db.commit()
    db.refresh(ep)
    return ep


@router.delete("/episodes/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_episode(episode_id: int, db: Session = Depends(get_db)):
    ep = db.get(Episode, episode_id)
    if ep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="集數不存在")
    db.delete(ep)
    db.commit()
