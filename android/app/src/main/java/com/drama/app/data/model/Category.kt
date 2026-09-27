package com.drama.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** GET /categories 回傳項 */
@Serializable
data class Category(
    val id: Int,
    val name: String,
    val slug: String? = null,
    val description: String? = null,
)
