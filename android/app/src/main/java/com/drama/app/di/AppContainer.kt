package com.drama.app.di

import android.content.Context
import com.drama.app.BuildConfig
import com.drama.app.data.api.ApiService
import com.drama.app.data.api.AuthInterceptor
import com.drama.app.data.repository.AuthRepository
import com.drama.app.data.repository.DramaRepository
import com.drama.app.data.repository.PlaybackRepository
import com.drama.app.util.TokenManager
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit

/**
 * 手動 DI 容器（不使用 Hilt）。
 * 在 Application 建立一次，整個 App 共用。
 */
class AppContainer(context: Context) {

    val tokenManager: TokenManager = TokenManager(context.applicationContext)

    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }

    private val okHttpClient: OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor(tokenManager))
        .addInterceptor(
            HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
        )
        .build()

    private val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL.trimEnd('/') + "/")
        .client(okHttpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    private val api: ApiService = retrofit.create(ApiService::class.java)

    val authRepository: AuthRepository = AuthRepository(api, tokenManager)
    val dramaRepository: DramaRepository = DramaRepository(api)
    val playbackRepository: PlaybackRepository = PlaybackRepository(api)
}
