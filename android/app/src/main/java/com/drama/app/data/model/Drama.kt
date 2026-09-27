package com.drama.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** 劇集列表項（GET /dramas 回傳陣列元素） */
@Serializable
data class Drama(
    val id: Int,
    val title: String,
    val description: String? = null,
    @SerialName("cover_url") val coverUrl: String? = null,
    @SerialName("category_id") val categoryId: Int? = null,
    @SerialName("release_year") val releaseYear: Int? = null,
    @SerialName("is_completed") val isCompleted: Boolean = false,
    @SerialName("category_name") val categoryName: String? = null,
    @SerialName("episode_count") val episodeCount: Int? = null,
    val category: Category? = null,
)

/** GET /dramas/{id} 回傳：含 episodes */
@Serializable
data class DramaDetail(
    val id: Int,
    val title: String,
    val description: String? = null,
    @SerialName("cover_url") val coverUrl: String? = null,
    @SerialName("category_id") val categoryId: Int? = null,
    @SerialName("release_year") val releaseYear: Int? = null,
    @SerialName("is_completed") val isCompleted: Boolean = false,
    @SerialName("category_name") val categoryName: String? = null,
    @SerialName("episode_count") val episodeCount: Int? = null,
    val category: Category? = null,
    val episodes: List<Episode> = emptyList(),
)

/**
 * 分類顯示名稱：優先取關聯物件 category.name，其次取後端 flat field category_name，
 * 都冇就 fallback「未分類」（同 web `drama.category?.name ?? drama.categoryName ?? '未分類'` 一致）。
 */
val Drama.categoryLabel: String
    get() = category?.name ?: categoryName ?: "未分類"

val DramaDetail.categoryLabel: String
    get() = category?.name ?: categoryName ?: "未分類"

/**
 * 分頁包裝（後端目前 /dramas 直接回傳陣列，此 model 保留以相容未來分頁格式）。
 */
@Serializable
data class PaginatedResponse<T>(
    val items: List<T> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    @SerialName("page_size") val pageSize: Int = 20,
)
