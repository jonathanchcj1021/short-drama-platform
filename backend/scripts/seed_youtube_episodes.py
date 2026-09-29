"""Seed：將 5 部原本只有 metadata（source='youku'、0 集）嘅劇，接入 YouTube 官方免費全集。

每部劇嘅每集 video id 已經由調查員從優酷官方 YouTube 頻道（YOUKU English /
YOUKU Mini Drama 等認證號）嘅官方 playlist 逐集核實（見 SOURCE_AUDIT_REPORT.md）。

Idempotent：已存在嘅集數（同 drama_id + episode_number）會跳過，可以安全重跑。

用法：
    DATABASE_URL=... .venv/bin/python -m scripts.seed_youtube_episodes
"""
from __future__ import annotations

from sqlalchemy import select

from app.database import SessionLocal
from app.models.drama import Drama
from app.models.episode import Episode

# drama_id -> [(episode_number, youtube_video_id), ...]
# video id 全部來自優酷官方認證 YouTube 頻道嘅官方 playlist（每條標題 | YOUKU）。
YOUTUBE_EPISODES: dict[int, list[tuple[int, str]]] = {
    # 67 锁爱三生（Circle of Love）— YOUKU English，playlist PLIPiKkS-FpK-zTWsxZO5xUAlAsUEFOl3K
    67: [
        (1, "Mt_o6K9Y59Q"), (2, "0e4PUE95gCk"), (3, "FGbciRJfGz8"), (4, "kVop_5QZ-cM"),
        (5, "NJXTCPVjSSI"), (6, "l-X8cA1yLAg"), (7, "NViayK1R56A"), (8, "V7m8WNX1gxE"),
        (9, "ps5CNXOsgSo"), (10, "RDNpQQwImv8"), (11, "Dv4_TvQgkZ8"), (12, "pZQA65WpwVI"),
        (13, "e5PHcB1S7Do"), (14, "tFCc6RnlOIs"), (15, "h9ybnZQRWA0"), (16, "ws_jHn0n9RE"),
        (17, "gHq2yLxeEDI"), (18, "qgd3lQqi7cw"), (19, "BGf1clB_uq0"), (20, "9WN3oWZ8LSY"),
        (21, "4J0PVfqNpXM"), (22, "LPA6cWd9vqA"), (23, "-Pfck_LVY64"), (24, "ydWeU4T8c1U"),
    ],
    # 60 我们在黑夜中相拥（Embrace in the Dark Night）— YOUKU English
    # playlist PLIPiKkS-FpK9bYBL2pbkmPeJ_BHwTuEDX（38 條 = 24 正片 + 預告/合輯，已剔除）
    60: [
        (1, "BVPQhfRwfUI"), (2, "wgiNonQtBuk"), (3, "y5imWTy-Ar4"), (4, "5HL-VsHjLY8"),
        (5, "RXkxQBlbaew"), (6, "guvDPT6SRr8"), (7, "zGXURF_vZvU"), (8, "Ce4Av1mA7bk"),
        (9, "_EzkSgZdheE"), (10, "luW_bo2-xTw"), (11, "haKtlKAxl3s"), (12, "iCxlyG-h3cA"),
        (13, "MBQmm2iT9vI"), (14, "nZKjAefTdzw"), (15, "W0pzz8paWq0"), (16, "diUffz37z_s"),
        (17, "V9Sjs5MvUIc"), (18, "ZD6_NdmsIYI"), (19, "OVnlO6sxVFs"), (20, "kBzK7gntigo"),
        (21, "3KDRrUOsds4"), (22, "u9d8cHU4C8s"), (23, "t_acesr_SHA"), (24, "tRH0SRLXaIU"),
    ],
    # 63 爱在天摇地动时（Undercover Affair）— YOUKU English
    # playlist PLIPiKkS-FpK9h3K-IncmKNfMmKM4TdqcM（24 條乾淨對應）
    63: [
        (1, "ipcnW-W5Fkg"), (2, "CUdzltp7lP0"), (3, "AB8a8hg7pLg"), (4, "y9DkouSH4to"),
        (5, "sqgkF2zc56E"), (6, "y5w-yVcpbSc"), (7, "xpnhJGUndos"), (8, "uLJQ-Qz348I"),
        (9, "A3MFb1ku3NY"), (10, "jafyALuXCJw"), (11, "MTKYsnjCslg"), (12, "uVeDlU_RJ9c"),
        (13, "QxDn-y6Cvlk"), (14, "AD9SfEyvGwk"), (15, "P5AwveWx2ls"), (16, "VO0IrUUnhas"),
        (17, "JakhjyGSaLI"), (18, "CEvc3e2oyPg"), (19, "XNopXTrzHhQ"), (20, "txjWFowCkpQ"),
        (21, "tts4T1t7ch8"), (22, "XsHU6NQKgPg"), (23, "olKLHOaFn0s"), (24, "94J4LOR1mZA"),
    ],
    # 64 永夜长明（Dawn is Breaking）— YOUKU English
    # playlist PLIPiKkS-FpK-BxGpxeLaoE3RK1-B27J2K（40 條 = 30 正片 + 預告/合輯，已剔除）
    64: [
        (1, "6YYeJcdHos4"), (2, "rXl_g4_1O4s"), (3, "vawGay9YgFc"), (4, "0sUb3_hR9ok"),
        (5, "z6MydktWpw0"), (6, "Vs9aa4SJyEc"), (7, "oCCnEf_gEA4"), (8, "45lv8Y1SRMI"),
        (9, "5i-tVfTFX1c"), (10, "ypbIF9XGhIY"), (11, "dEjyH7Gg_js"), (12, "2jKJSKq-qlI"),
        (13, "YMOgiymZf9Y"), (14, "l4414iJCE_U"), (15, "h0HxHdwlxaQ"), (16, "G451cOmMu14"),
        (17, "78BUGN7wbMw"), (18, "WQYgPqXxu0s"), (19, "YSNfsYerNUY"), (20, "_EWNCtfmVN8"),
        (21, "Z6PRnPZlQGU"), (22, "zGVuGGLHnk4"), (23, "Rz2uuoluMvE"), (24, "t3ijLSiWkc8"),
        (25, "RCEnLrOK2Nk"), (26, "CrW7GBI1QD4"), (27, "bvU6LqhG0nI"), (28, "ixABUsYwTeM"),
        (29, "rSlp4Sh6mdQ"), (30, "xTqe-h63puw"),
    ],
    # 66 千金丫环（Maid's Revenge）— YOUKU Mini Drama
    # playlist PLogLib6e6DfRzv1GvGLaaa_0pgXhmiQ5-（39 條 = 30 正片 + 合輯/花絮，已剔除）
    66: [
        (1, "ct0kqNJkfVg"), (2, "anoSHaeW5Q8"), (3, "42h6S5TCNS4"), (4, "JLVeIA8eB18"),
        (5, "gfwYDNGBjF0"), (6, "1rcXqEnIrxc"), (7, "d-4Cu5Mukmw"), (8, "BULpIYb7smE"),
        (9, "ad3tkkBjnJo"), (10, "9Up9jwHOMl8"), (11, "ZoknZ0CKS_U"), (12, "xtLnOTAVAKQ"),
        (13, "1ceXNXRpnLM"), (14, "T3vGrnlRH2Y"), (15, "8EBCFtonQBs"), (16, "3Mt6UyP-F1g"),
        (17, "jrUvyWQ-quM"), (18, "lh1tqmhfqQU"), (19, "s8vtrmTPj9U"), (20, "Df2gka3qP2Y"),
        (21, "MLzYtWqBOa8"), (22, "ODD9Gc7dS5g"), (23, "wuUwlWyu4WU"), (24, "o_zcrMzkwl8"),
        (25, "lePGarSHbsw"), (26, "ZesauPqe974"), (27, "noA-_BhcVOA"), (28, "OfFfucmruC0"),
        (29, "3brK1vODJzI"), (30, "UnujCfuuk2s"),
    ],
}


def main() -> None:
    db = SessionLocal()
    created_total = 0
    try:
        for drama_id, eps in YOUTUBE_EPISODES.items():
            drama = db.get(Drama, drama_id)
            if drama is None:
                print(f"[WARN] drama_id={drama_id} 唔存在，跳過")
                continue

            created = 0
            skipped = 0
            for ep_num, vid in eps:
                existing = db.scalar(
                    select(Episode).where(
                        Episode.drama_id == drama_id,
                        Episode.episode_number == ep_num,
                    )
                )
                if existing is not None:
                    skipped += 1
                    continue
                db.add(
                    Episode(
                        drama_id=drama_id,
                        episode_number=ep_num,
                        title=f"第 {ep_num} 集",
                        video_url=f"https://www.youtube.com/watch?v={vid}",
                        video_type="youtube",
                    )
                )
                created += 1

            # 來源切到 youtube（idempotent）
            if drama.source != "youtube":
                drama.source = "youtube"
            db.commit()
            print(
                f"drama {drama_id} 《{drama.title}》: 新建 {created} 集，"
                f"已存在跳過 {skipped} 集，source={drama.source}"
            )
            created_total += created

        print(f"\n完成：今次新建 {created_total} 集 YouTube episode rows。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
