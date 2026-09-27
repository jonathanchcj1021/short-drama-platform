"""匯入所有模型，讓 Base.metadata 能完整探索。"""
from app.models.category import Category  # noqa: F401
from app.models.drama import Drama  # noqa: F401
from app.models.episode import Episode  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.watch_progress import WatchProgress  # noqa: F401
