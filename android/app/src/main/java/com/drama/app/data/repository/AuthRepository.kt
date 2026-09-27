package com.drama.app.data.repository

import com.drama.app.data.api.ApiService
import com.drama.app.data.model.OtpRequest
import com.drama.app.data.model.OtpVerify
import com.drama.app.util.TokenManager

class AuthRepository(
    private val api: ApiService,
    private val tokenManager: TokenManager,
) {
    /** 是否已登入（本機有 access token）。 */
    val isLoggedIn: Boolean get() = tokenManager.accessToken != null

    val currentPhone: String? get() = tokenManager.phoneNumber

    suspend fun requestOtp(phoneNumber: String) {
        api.requestOtp(OtpRequest(phoneNumber = phoneNumber))
        // 記住手機號，供登入成功後顯示。
        tokenManager.phoneNumber = phoneNumber
    }

    /** 驗證成功後儲存 token，回傳是否成功。 */
    suspend fun verifyOtp(phoneNumber: String, code: String): Boolean {
        val tokens = api.verifyOtp(OtpVerify(phoneNumber = phoneNumber, code = code))
        tokenManager.saveTokens(
            accessToken = tokens.accessToken,
            refreshToken = tokens.refreshToken,
        )
        tokenManager.phoneNumber = tokens.user?.phoneNumber ?: phoneNumber
        return true
    }

    /**
     * Google SSO（WebView fallback）：從 OAuth redirect fragment 取出嘅
     * access_token / refresh_token 存入 TokenManager，之後再打 /auth/me 攞 user。
     */
    suspend fun saveGoogleTokens(accessToken: String, refreshToken: String): Boolean {
        tokenManager.saveTokens(accessToken, refreshToken)
        return true
    }

    suspend fun me() = api.me()

    fun logout() = tokenManager.clear()
}
