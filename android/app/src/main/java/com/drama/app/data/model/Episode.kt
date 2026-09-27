package com.drama.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** 集數（GET /episodes/{id}、DramaDetail.episodes 項目） */
@Serializable
data class Episode(
    val id: Int,
    @SerialName("drama_id") val dramaId: Int,
    @SerialName("episode_number") val episodeNumber: Int,
    val title: String,
    @SerialName("video_url") val videoUrl: String,
    /** 秒 */
    val duration: Int? = null,
    val description: String? = null,
)

/** GET /episodes/{id}/stream 回傳 */
@Serializable
data class StreamResponse(
    val episode: Episode,
    @SerialName("video_url") val videoUrl: String,
)
