package com.drama.app.data.repository

import com.drama.app.data.api.ApiService
import com.drama.app.data.model.Category
import com.drama.app.data.model.Drama
import com.drama.app.data.model.DramaDetail
import com.drama.app.data.model.ProgressResponse

class DramaRepository(
    private val api: ApiService,
) {
    suspend fun categories(): List<Category> = api.categories()

    suspend fun dramas(categoryId: Int? = null): List<Drama> =
        api.dramas(categoryId = categoryId, skip = 0, limit = 20)

    suspend fun dramaDetail(id: Int): DramaDetail = api.dramaDetail(id)

    /** 需登入；未登入會丟出 exception（由 UI 層處理）。 */
    suspend fun dramaProgress(id: Int): List<ProgressResponse> = api.dramaProgress(id)
}
