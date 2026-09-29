"""CMS 路由：寫操作（需管理員權限）。"""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_db, require_admin
from app.models.ad import Ad
from app.models.category import Category
from app.models.drama import Drama
from app.models.episode import Episode
from app.models.user import User
from app.schemas.ad import AdOut, AdUpdate
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.schemas.drama import DramaCreate, DramaOut, DramaUpdate
from app.schemas.episode import EpisodeCreate, EpisodeOut, EpisodeUpdate

router = APIRouter(prefix="/cms", tags=["cms"], dependencies=[Depends(require_admin)])

# 廣告影片存放目錄（掛載喺 /static 之下）
ADS_DIR = Path(__file__).resolve().parent.parent / "static" / "ads"
ALLOWED_AD_EXT = ".mp4"
ALLOWED_AD_MIME = "video/mp4"


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


# ---------- Ads（廣告影片上傳與管理） ----------
@router.post("/ads/upload", response_model=AdOut, status_code=status.HTTP_201_CREATED)
def upload_ad(
    file: UploadFile = File(...),
    title: str = Form(...),
    duration: int = Form(20),
    db: Session = Depends(get_db),
):
    """上傳廣告影片（multipart/form-data），存落 static/ads/ 並記一筆 Ad。"""
    title = title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="標題不能空白")

    # 副檔名 + MIME 雙重檢查，只收 mp4
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext != ALLOWED_AD_EXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="只接受 .mp4 影片檔"
        )
    if file.content_type and file.content_type != ALLOWED_AD_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="只接受 video/mp4 影片檔"
        )

    ADS_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex[:8]}{ALLOWED_AD_EXT}"
    dest = ADS_DIR / stored_name
    with dest.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    video_url = f"/static/ads/{stored_name}"
    ad = Ad(title=title, video_url=video_url, duration=duration, active=True)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


@router.get("/ads", response_model=list[AdOut])
def list_ads(db: Session = Depends(get_db)):
    stmt = select(Ad).order_by(Ad.id.desc())
    return db.scalars(stmt).all()


@router.put("/ads/{ad_id}", response_model=AdOut)
def update_ad(ad_id: int, body: AdUpdate, db: Session = Depends(get_db)):
    ad = db.get(Ad, ad_id)
    if ad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="廣告不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(ad, k, v)
    db.commit()
    db.refresh(ad)
    return ad


@router.delete("/ads/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.get(Ad, ad_id)
    if ad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="廣告不存在")
    # 一併刪除 static/ads 對應檔案
    rel = ad.video_url.removeprefix("/static/")
    static_root = Path(__file__).resolve().parent.parent / "static"
    fpath = static_root / rel
    if fpath.is_file():
        fpath.unlink()
    db.delete(ad)
    db.commit()
