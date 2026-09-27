package com.drama.app.ui.login

import android.annotation.SuppressLint
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.drama.app.BuildConfig
import com.drama.app.di.AppContainer
import com.drama.app.ui.theme.AccentHover
import com.drama.app.ui.theme.AccentPress
import com.drama.app.ui.theme.BgPrimary
import com.drama.app.ui.theme.TextOnAccent
import com.drama.app.ui.theme.TextSecondary
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    container: AppContainer,
    onLoggedIn: () -> Unit,
) {
    var phone by remember { mutableStateOf("") }
    var code by remember { mutableStateOf("") }
    var codeSent by remember { mutableStateOf(false) }
    var cooldown by mutableIntStateOf(0)
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var showGoogleWebView by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    // 60 秒倒數
    LaunchedEffect(codeSent) {
        if (codeSent) {
            cooldown = 60
            while (cooldown > 0) {
                delay(1000L)
                cooldown -= 1
            }
        }
    }

    if (showGoogleWebView) {
        GoogleOAuthWebView(
            container = container,
            onSuccess = onLoggedIn,
            onClose = { showGoogleWebView = false },
            onError = { msg ->
                error = msg
                showGoogleWebView = false
            },
        )
        return
    }

    Scaffold(topBar = { TopAppBar(title = { Text("登入短劇平台") }) }) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("歡迎回來", style = MaterialTheme.typography.headlineMedium)
            Spacer(Modifier.height(24.dp))

            // ---- Google SSO（白底黑字，左邊 Google G icon）----
            GoogleSignInButton(onClick = { showGoogleWebView = true })
            Spacer(Modifier.height(16.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.weight(1f).height(1.dp).background(TextSecondary.copy(alpha = 0.3f)))
                Text(
                    "或使用手機號碼登入",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    modifier = Modifier.padding(horizontal = 12.dp),
                )
                Box(Modifier.weight(1f).height(1.dp).background(TextSecondary.copy(alpha = 0.3f)))
            }
            Spacer(Modifier.height(16.dp))

            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it.filter { c -> c.isDigit() || c == '+' } },
                label = { Text("手機號碼") },
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(Modifier.height(12.dp))

            // 發送驗證碼按鈕（含倒數冷卻），紅漸層主鈕
            GradientButton(
                text = if (codeSent) "驗證碼已發送" else "發送驗證碼",
                onClick = {
                    if (phone.isBlank()) return@GradientButton
                    busy = true
                    error = null
                    scope.launch {
                        runCatching { container.authRepository.requestOtp(phone.trim()) }
                            .onSuccess { codeSent = true }
                            .onFailure { error = "發送失敗：${it.localizedMessage}" }
                        busy = false
                    }
                },
                enabled = !busy && !codeSent,
            )
            if (codeSent) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = if (cooldown > 0) "${cooldown} 秒後可重發" else "可重新發送",
                    style = MaterialTheme.typography.bodySmall,
                )
            }

            if (codeSent) {
                Spacer(Modifier.height(16.dp))
                OutlinedTextField(
                    value = code,
                    onValueChange = { code = it.filter { c -> c.isDigit() }.take(6) },
                    label = { Text("6 位驗證碼") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth(),
                )
                Spacer(Modifier.height(12.dp))
                GradientButton(
                    text = "驗證登入",
                    onClick = {
                        if (code.length != 6) return@GradientButton
                        busy = true
                        error = null
                        scope.launch {
                            runCatching { container.authRepository.verifyOtp(phone.trim(), code) }
                                .onSuccess { onLoggedIn() }
                                .onFailure { error = "驗證失敗：${it.localizedMessage}" }
                            busy = false
                        }
                    },
                    enabled = !busy && code.length == 6,
                )
            }

            if (busy) {
                Spacer(Modifier.height(16.dp))
                CircularProgressIndicator()
            }
            error?.let {
                Spacer(Modifier.height(16.dp))
                Text(it, color = MaterialTheme.colorScheme.error)
            }
        }
    }
}

/** 紅漸層主鈕（對應 web `--gradient-accent`）。 */
@Composable
private fun GradientButton(
    text: String,
    onClick: () -> Unit,
    enabled: Boolean = true,
) {
    val brush = if (enabled) {
        Brush.linearGradient(listOf(AccentHover, AccentPress))
    } else {
        Brush.linearGradient(listOf(Color(0xFF555555), Color(0xFF555555)))
    }
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(brush)
            .clickable(enabled = enabled, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text,
            color = TextOnAccent,
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(vertical = 14.dp),
        )
    }
}

/** 白底黑字 Google 登入鈕（左邊一個簡化 G icon，唔依賴外部 drawable）。 */
@Composable
private fun GoogleSignInButton(onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(10.dp),
        color = Color.White,
        modifier = Modifier.fillMaxWidth().height(48.dp),
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            // 簡化 Google G：小方塊漸層（唔引入官方 vector drawable）
            Box(
                modifier = Modifier
                    .width(20.dp).height(20.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(Brush.linearGradient(listOf(Color(0xFF4285F4), Color(0xFF34A853)))),
                contentAlignment = Alignment.Center,
            ) {
                Text("G", color = Color.White, style = MaterialTheme.typography.titleSmall)
            }
            Spacer(Modifier.width(12.dp))
            Text("使用 Google 帳號登入", color = Color(0xFF1F1F1F), style = MaterialTheme.typography.titleMedium)
        }
    }
}

/**
 * Google OAuth WebView fallback：
 * 後端而家 redirect 指去 web SPA（帶 `#access_token=...&refresh_token=...` fragment），
 * 所以喺 app 內開 WebView 載 authorize URL，喺 shouldOverrideUrlLoading 偵測 fragment、
 * 攔截、解析 token、存入 TokenManager、打 /auth/me、導去 Home。
 */
@SuppressLint("SetJavaScriptEnabled")
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun GoogleOAuthWebView(
    container: AppContainer,
    onSuccess: () -> Unit,
    onClose: () -> Unit,
    onError: (String) -> Unit,
) {
    val scope = rememberCoroutineScope()
    var done by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Google 登入") },
                navigationIcon = {
                    IconButton(onClick = onClose) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
            )
        },
        containerColor = BgPrimary,
    ) { padding ->
        AndroidView(
            modifier = Modifier.fillMaxSize().padding(padding),
            factory = { ctx ->
                WebView(ctx).apply {
                    settings.javaScriptEnabled = true
                    settings.domStorageEnabled = true
                    settings.databaseEnabled = true
                    webViewClient = object : WebViewClient() {
                        override fun shouldOverrideUrlLoading(
                            view: WebView?,
                            request: WebResourceRequest?,
                        ): Boolean {
                            val raw = request?.url?.toString() ?: return false
                            // 偵測 redirect 帶 access_token fragment
                            if (raw.contains("#access_token=")) {
                                if (done) return true
                                done = true
                                val frag = request.url?.fragment.orEmpty()
                                val params = frag.split("&")
                                    .mapNotNull { kv ->
                                        val idx = kv.indexOf('=')
                                        if (idx <= 0) null
                                        else kv.substring(0, idx) to kv.substring(idx + 1)
                                    }
                                    .toMap()
                                val access = params["access_token"]
                                val refresh = params["refresh_token"] ?: ""
                                if (access.isNullOrEmpty()) {
                                    onError("無法從回呼網址取出 access_token")
                                    return true
                                }
                                scope.launch {
                                    runCatching {
                                        container.authRepository.saveGoogleTokens(access, refresh)
                                        container.authRepository.me()
                                    }.onSuccess { onSuccess() }
                                     .onFailure { onError("Google 登入失敗：${it.localizedMessage}") }
                                }
                                return true
                            }
                            return false
                        }
                    }
                    loadUrl("${BuildConfig.API_BASE_URL}/auth/google/authorize")
                }
            },
        )
    }
}
