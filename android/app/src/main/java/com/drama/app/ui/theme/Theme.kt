package com.drama.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColors = darkColorScheme(
    primary = DramaAccent,
    secondary = PurpleGrey80,
    background = DramaDark,
    surface = DramaDark,
)

private val LightColors = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
)

@Composable
fun ShortDramaTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    // 短劇 App 預設走深色（看影片情境），仍跟隨系統切換。
    val colors = if (darkTheme) DarkColors else LightColors
    MaterialTheme(
        colorScheme = colors,
        typography = Typography,
        content = content,
    )
}
