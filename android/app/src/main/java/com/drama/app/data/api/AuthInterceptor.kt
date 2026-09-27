package com.drama.app.data.api

import com.drama.app.util.TokenManager
import okhttp3.Interceptor
import okhttp3.Response

/**
 * 自動帶 Authorization: Bearer <access_token>。
 * 收到 401 時清除 token，並透過 tokenManager 廣播「未授權」事件，
 * 讓 UI 層（AppNavigation）統一導回登入頁。
 */
class AuthInterceptor(
    private val tokenManager: TokenManager,
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val builder = chain.request().newBuilder()
        tokenManager.accessToken?.let { token ->
            builder.header("Authorization", "Bearer $token")
        }
        val response = chain.proceed(builder.build())
        if (response.code == 401) {
            tokenManager.onUnauthorized()
        }
        return response
    }
}
