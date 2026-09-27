package com.drama.app.ui.play

import android.net.Uri
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import com.drama.app.BuildConfig
import com.drama.app.data.model.StreamResponse
import com.drama.app.di.AppContainer
import com.drama.app.util.Constants
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PlayScreen(
    container: AppContainer,
    episodeId: Int,
    dramaId: Int,
    onBack: () -> Unit,
    onSwitchEpisode: (Int) -> Unit,
) {
    val context = LocalContext.current

    var stream by remember { mutableStateOf<StreamResponse?>(null) }
    var episodes by remember { mutableStateOf<List<com.drama.app.data.model.Episode>>(emptyList()) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    val exoPlayer = remember {
        ExoPlayer.Builder(context).build()
    }

    // 取得串流 + 該劇所有集數（供上下集切換）
    LaunchedEffect(episodeId) {
        loading = true
        error = null
        runCatching { container.playbackRepository.stream(episodeId) }
            .onSuccess { s ->
                stream = s
                val url = resolveUrl(s.videoUrl)
                exoPlayer.setMediaItem(MediaItem.fromUri(url))
                exoPlayer.prepare()
                exoPlayer.playWhenReady = true
            }
            .onFailure { error = "無法載入影片：${it.localizedMessage}" }
        // 取劇集詳情以建立上下集清單
        runCatching { container.dramaRepository.dramaDetail(dramaId) }
            .onSuccess { episodes = it.episodes.sortedBy { e -> e.episodeNumber } }
        loading = false
    }

    // 每 10 秒回報進度
    LaunchedEffect(episodeId) {
        while (true) {
            delay(Constants.PROGRESS_REPORT_INTERVAL_MS)
            val pos = exoPlayer.currentPosition / 1000
            val dur = exoPlayer.duration.takeIf { it > 0 }?.let { it / 1000 }
            val completed = exoPlayer.playbackState == ExoPlayer.STATE_ENDED
            runCatching {
                container.playbackRepository.reportProgress(
                    episodeId = episodeId,
                    currentTime = pos.toInt(),
                    duration = dur?.toInt(),
                    completed = completed,
                )
            }
        }
    }

    // 離開畫面釋放播放器
    DisposableEffect(Unit) {
        onDispose { exoPlayer.release() }
    }

    val idx = episodes.indexOfFirst { it.id == episodeId }
    val prev = if (idx > 0) episodes[idx - 1] else null
    val next = if (idx in 0 until episodes.size - 1) episodes[idx + 1] else null

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stream?.episode?.title ?: "播放中") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
            )
        },
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding)) {
            // 16:9 播放器
            Box(
                Modifier
                    .fillMaxWidth()
                    .aspectRatio(16f / 9f),
                contentAlignment = Alignment.Center,
            ) {
                if (loading) {
                    CircularProgressIndicator()
                } else if (error != null) {
                    Text(error!!, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(16.dp))
                } else {
                    AndroidView(
                        factory = { ctx ->
                            PlayerView(ctx).apply { player = exoPlayer }
                        },
                        modifier = Modifier.fillMaxSize(),
                    )
                }
            }

            Column(Modifier.padding(16.dp)) {
                stream?.let {
                    Text("第 ${it.episode.episodeNumber} 集", style = MaterialTheme.typography.titleMedium)
                    it.episode.duration?.let { d ->
                        Text("時長 ${d / 60} 分 ${d % 60} 秒", style = MaterialTheme.typography.bodySmall)
                    }
                }
                Spacer(Modifier.height(16.dp))
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                ) {
                    OutlinedButton(
                        onClick = { prev?.let { onSwitchEpisode(it.id) } },
                        enabled = prev != null,
                    ) { Text("上一集") }
                    OutlinedButton(
                        onClick = { next?.let { onSwitchEpisode(it.id) } },
                        enabled = next != null,
                    ) { Text("下一集") }
                }
            }
        }
    }
}

/** 相對路徑（"/uploads/xx.mp4"）補上 API base；完整 URL 直接使用。 */
private fun resolveUrl(raw: String): String {
    if (raw.startsWith("http://") || raw.startsWith("https://")) return raw
    val base = BuildConfig.API_BASE_URL.trimEnd('/')
    return if (raw.startsWith("/")) "$base$raw" else "$base/$raw"
}
