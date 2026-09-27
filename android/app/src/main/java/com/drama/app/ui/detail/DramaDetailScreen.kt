package com.drama.app.ui.detail

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.drama.app.data.model.DramaDetail
import com.drama.app.data.model.Episode
import com.drama.app.data.model.ProgressResponse
import com.drama.app.di.AppContainer
import com.drama.app.util.Constants

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DramaDetailScreen(
    container: AppContainer,
    dramaId: Int,
    onBack: () -> Unit,
    onPlayEpisode: (Int) -> Unit,
) {
    var detail by remember { mutableStateOf<DramaDetail?>(null) }
    var progress by remember { mutableStateOf<List<ProgressResponse>>(emptyList()) }
    var loading by remember { mutableStateOf(true) }

    LaunchedEffect(dramaId) {
        runCatching { container.dramaRepository.dramaDetail(dramaId) }
            .onSuccess { detail = it }
        // 觀看進度（需登入；失敗就略過）
        runCatching { container.dramaRepository.dramaProgress(dramaId) }
            .onSuccess { progress = it }
        loading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(detail?.title ?: "劇集詳情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
            )
        },
    ) { padding ->
        if (loading) {
            Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            return@Scaffold
        }
        val d = detail ?: return@Scaffold

        LazyColumn(
            Modifier.fillMaxSize().padding(padding),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
        ) {
            item {
                AsyncImage(
                    model = d.coverUrl ?: Constants.PLACEHOLDER_COVER,
                    contentDescription = d.title,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(16f / 9f),
                )
                Spacer(Modifier.height(16.dp))
                Text(d.title, style = MaterialTheme.typography.headlineSmall)
                Text(
                    "${d.category?.name ?: "未分類"}${d.releaseYear?.let { " · $it" } ?: ""}",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Spacer(Modifier.height(8.dp))
                Text(d.description ?: "暫無介紹", style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(16.dp))
                Text("集數（${d.episodes.size}）", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
            }
            items(d.episodes) { ep ->
                EpisodeRow(
                    episode = ep,
                    progressSeconds = progress.firstOrNull { it.episodeId == ep.id }?.currentTime,
                    onClick = { onPlayEpisode(ep.id) },
                )
            }
        }
    }
}

@Composable
private fun EpisodeRow(episode: Episode, progressSeconds: Int?, onClick: () -> Unit) {
    Card(onClick = onClick, modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(
                "第 ${episode.episodeNumber} 集",
                style = MaterialTheme.typography.titleSmall,
            )
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(episode.title, style = MaterialTheme.typography.bodyMedium)
                episode.duration?.let {
                    Text("時長 ${it / 60}:${(it % 60).toString().padStart(2, '0')}",
                        style = MaterialTheme.typography.bodySmall)
                }
            }
            if (progressSeconds != null && progressSeconds > 5) {
                Text(
                    "已看 ${progressSeconds / 60} 分",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}
