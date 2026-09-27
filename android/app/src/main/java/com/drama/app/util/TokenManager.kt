package com.drama.app.util

import android.content.Context
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow

/**
 * SharedPreferences 包裝：儲存 access / refresh token 與手機號。
 * 另對外廣播「未授權」事件（收到 401 時），供導回登入頁。
 */
class TokenManager(context: Context) {

    private val prefs = context.getSharedPreferences("drama_prefs", Context.MODE_PRIVATE)

    var accessToken: String?
        get() = prefs.getString(KEY_ACCESS, null)
        set(value) = prefs.edit().putString(KEY_ACCESS, value).apply()

    var refreshToken: String?
        get() = prefs.getString(KEY_REFRESH, null)
        set(value) = prefs.edit().putString(KEY_REFRESH, value).apply()

    var phoneNumber: String?
        get() = prefs.getString(KEY_PHONE, null)
        set(value) = prefs.edit().putString(KEY_PHONE, value).apply()

    fun saveTokens(accessToken: String, refreshToken: String) {
        prefs.edit()
            .putString(KEY_ACCESS, accessToken)
            .putString(KEY_REFRESH, refreshToken)
            .apply()
    }

    fun clear() {
        prefs.edit().clear().apply()
    }

    private val _unauthorizedEvents = MutableSharedFlow<Unit>(extraBufferCapacity = 1)
    val unauthorizedEvents: SharedFlow<Unit> = _unauthorizedEvents.asSharedFlow()

    /** 收到 401：清除本機登入狀態並廣播。 */
    fun onUnauthorized() {
        clear()
        _unauthorizedEvents.tryEmit(Unit)
    }

    companion object {
        private const val KEY_ACCESS = "access_token"
        private const val KEY_REFRESH = "refresh_token"
        private const val KEY_PHONE = "phone_number"
    }
}
