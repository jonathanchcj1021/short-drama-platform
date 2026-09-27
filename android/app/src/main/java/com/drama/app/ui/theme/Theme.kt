package com.drama.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

// 短劇 App 情境係睇片，強制深色，唔跟系統淺色。
private val DarkColors = darkColorScheme(
    primary       = Accent,
    onPrimary     = TextOnAccent,
    secondary     = Gold,
    background    = BgPrimary,
    onBackground  = TextPrimary,
    surface       = Surface,
    onSurface     = TextPrimary,
    surfaceVariant= SurfaceRaised,
    onSurfaceVariant = TextSecondary,
    error         = ErrorC,
    onError       = TextOnAccent,
)

@Composable
fun ShortDramaTheme(
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = DarkColors,
        typography = DramaTypography,
        content = content,
    )
}
