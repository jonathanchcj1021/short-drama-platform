package com.drama.app.data.api

import com.drama.app.data.model.AccessTokenResponse
import com.drama.app.data.model.Category
import com.drama.app.data.model.Drama
import com.drama.app.data.model.DramaDetail
import com.drama.app.data.model.Episode
import com.drama.app.data.model.OtpRequest
import com.drama.app.data.model.OtpVerify
import com.drama.app.data.model.ProgressRequest
import com.drama.app.data.model.ProgressResponse
import com.drama.app.data.model.RefreshTokenRequest
import com.drama.app.data.model.StreamResponse
import com.drama.app.data.model.TokenResponse
import com.drama.app.data.model.UserOut
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

/** 後端 API 端點。base URL 由 BuildConfig.API_BASE_URL 注入。 */
interface ApiService {

    // ---- Auth ----
    @POST("auth/otp/request")
    suspend fun requestOtp(@Body body: OtpRequest): Map<String, String>

    @POST("auth/otp/verify")
    suspend fun verifyOtp(@Body body: OtpVerify): TokenResponse

    @POST("auth/refresh")
    suspend fun refresh(@Body body: RefreshTokenRequest): AccessTokenResponse

    @GET("auth/me")
    suspend fun me(): UserOut

    // ---- Categories ----
    @GET("categories")
    suspend fun categories(): List<Category>

    // ---- Dramas ----
    @GET("dramas")
    suspend fun dramas(
        @Query("category_id") categoryId: Int? = null,
        @Query("search") search: String? = null,
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 20,
    ): List<Drama>

    @GET("dramas/{id}")
    suspend fun dramaDetail(@Path("id") id: Int): DramaDetail

    @GET("dramas/{id}/progress")
    suspend fun dramaProgress(@Path("id") id: Int): List<ProgressResponse>

    // ---- Episodes ----
    @GET("episodes/{id}")
    suspend fun episode(@Path("id") id: Int): Episode

    @GET("episodes/{id}/stream")
    suspend fun stream(@Path("id") id: Int): StreamResponse

    @POST("episodes/{id}/progress")
    suspend fun reportProgress(
        @Path("id") id: Int,
        @Body body: ProgressRequest,
    ): ProgressResponse
}
