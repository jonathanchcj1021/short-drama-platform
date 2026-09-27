package com.drama.app.data.repository

import com.drama.app.data.api.ApiService
import com.drama.app.data.model.StreamResponse

class PlaybackRepository(
    private val api: ApiService,
) {
    /** 取得串流資訊（含 video_url）。需登入。 */
    suspend fun stream(episodeId: Int): StreamResponse = api.stream(episodeId)

    /** 上報觀看進度。 */
    suspend fun reportProgress(episodeId: Int, currentTime: Int, duration: Int?, completed: Boolean) {
        api.reportProgress(
            episodeId = episodeId,
            body = com.drama.app.data.model.ProgressRequest(
                currentTime = currentTime,
                duration = duration,
                completed = completed,
            ),
        )
    }
}
