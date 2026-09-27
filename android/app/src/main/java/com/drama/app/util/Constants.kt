package com.drama.app.util

/** 全域常數。 */
object Constants {
    /** 預設佔位封面（後端無 cover_url 時使用）。 */
    const val PLACEHOLDER_COVER = "https://picsum.photos/seed/drama/600/900"

    /** 進度上報間隔（毫秒）：每 10 秒。 */
    const val PROGRESS_REPORT_INTERVAL_MS = 10_000L

    /** OTP 倒數冷卻（秒）。 */
    const val OTP_COOLDOWN_SECONDS = 60
}
