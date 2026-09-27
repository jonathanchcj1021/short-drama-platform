package com.drama.app.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.drama.app.di.AppContainer
import com.drama.app.util.Constants
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
    var cooldown by remember { mutableIntStateOf(0) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    // 60 秒倒數
    LaunchedEffect(codeSent) {
        if (codeSent) {
            cooldown = Constants.OTP_COOLDOWN_SECONDS
            while (cooldown > 0) {
                delay(1000L)
                cooldown -= 1
            }
        }
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

            OutlinedTextField(
                value = phone,
                onValueChange = { phone = it.filter { c -> c.isDigit() || c == '+' } },
                label = { Text("手機號碼") },
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(Modifier.height(12.dp))

            // 發送驗證碼按鈕（含倒數冷卻）
            Button(
                onClick = {
                    if (phone.isBlank()) return@Button
                    busy = true
                    error = null
                    scope.launch {
                        runCatching { container.authRepository.requestOtp(phone.trim()) }
                            .onSuccess {
                                codeSent = true
                            }
                            .onFailure { error = "發送失敗：${it.localizedMessage}" }
                        busy = false
                    }
                },
                enabled = !busy && !codeSent,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(if (codeSent) "驗證碼已發送" else "發送驗證碼")
            }
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
                Button(
                    onClick = {
                        if (code.length != 6) return@Button
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
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("驗證登入")
                }
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
