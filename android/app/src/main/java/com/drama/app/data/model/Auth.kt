package com.drama.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/** POST /auth/otp/request body */
@Serializable
data class OtpRequest(
    @SerialName("phone_number") val phoneNumber: String,
)

/** POST /auth/otp/verify body */
@Serializable
data class OtpVerify(
    @SerialName("phone_number") val phoneNumber: String,
    val code: String,
)

/** POST /auth/refresh body */
@Serializable
data class RefreshTokenRequest(
    @SerialName("refresh_token") val refreshToken: String,
)

/** 目前使用者（GET /auth/me） */
@Serializable
data class UserOut(
    val id: Int,
    @SerialName("phone_number") val phoneNumber: String,
    val nickname: String? = null,
)

/** POST /auth/otp/verify 回傳 */
@Serializable
data class TokenResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String,
    @SerialName("token_type") val tokenType: String = "bearer",
    val user: UserOut? = null,
)

/** POST /auth/refresh 回傳 */
@Serializable
data class AccessTokenResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String = "bearer",
)
