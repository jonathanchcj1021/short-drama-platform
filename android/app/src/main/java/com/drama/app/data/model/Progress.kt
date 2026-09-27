package com.drama.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** POST /episodes/{id}/progress body */
@Serializable
data class ProgressRequest(
    @SerialName("current_time") val currentTime: Int,
    /** 秒，可為 null */
    val duration: Int? = null,
    val completed: Boolean = false,
)

/** 進度回傳（POST progress / GET dramas/{id}/progress 項目） */
@Serializable
data class ProgressResponse(
    @SerialName("episode_id") val episodeId: Int,
    @SerialName("current_time") val currentTime: Int,
    val duration: Int? = null,
    val completed: Boolean = false,
    @SerialName("updated_at") val updatedAt: String? = null,
)
