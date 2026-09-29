package com.drama.app.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.drama.app.BuildConfig
import com.drama.app.data.model.Category
import com.drama.app.data.model.Drama
import com.drama.app.data.model.categoryLabel
import com.drama.app.di.AppContainer
import com.drama.app.ui.theme.Accent
import com.drama.app.ui.theme.AccentHover
import com.drama.app.ui.theme.AccentPress
import com.drama.app.ui.theme.BgPrimary
import com.drama.app.ui.theme.BorderDefault
import com.drama.app.ui.theme.Surface
import com.drama.app.ui.theme.SurfaceRaised
import com.drama.app.ui.theme.TextOnAccent
import com.drama.app.ui.theme.TextPrimary
import com.drama.app.ui.theme.TextSecondary
import com.drama.app.util.Constants
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    container: AppContainer,
    onOpenDrama: (Int) -> Unit,
) {
    var categories by remember { mutableStateOf<List<Category>>(emptyList()) }
    var selectedCategory by remember { mutableStateOf<Int?>(null) }
    var dramas by remember { mutableStateOf<List<Drama>>(emptyList()) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    var menuExpanded by remember { mutableStateOf(false) }
    var showAbout by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    // 載入分類
    LaunchedEffect(Unit) {
        runCatching { container.dramaRepository.categories() }
            .onSuccess { categories = it }
            .onFailure { /* 分類失敗不致命，略過 */ }
    }

    // 載入劇集（依分類篩選）
    LaunchedEffect(selectedCategory) {
        loading = true
        error = null
        runCatching { container.dramaRepository.dramas(selectedCategory) }
            .onSuccess { dramas = it }
            .onFailure { error = "載入失敗：${it.localizedMessage}" }
        loading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        // logo mark：24dp 圓角 6dp 紅漸層小方塊
                        Box(
                            modifier = Modifier
                                .size(24.dp)
                                .clip(RoundedCornerShape(6.dp))
                                .background(Brush.linearGradient(listOf(AccentHover, AccentPress))),
                        )
                        androidx.compose.foundation.layout.Spacer(Modifier.width(10.dp))
                        Column {
                            Text("短劇平台", color = TextPrimary)
                            container.authRepository.currentPhone?.let {
                                Text(it, style = MaterialTheme.typography.bodySmall, color = TextSecondary)
                            }
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BgPrimary.copy(alpha = 0.85f),
                    scrolledContainerColor = BgPrimary,
                    titleContentColor = TextPrimary,
                ),
                actions = {
                    IconButton(onClick = { menuExpanded = true }) {
                        Icon(Icons.Default.MoreVert, contentDescription = "選單")
                    }
                    DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) {
                        DropdownMenuItem(
                            text = { Text("關於", color = TextSecondary) },
                            onClick = {
                                menuExpanded = false
                                showAbout = true
                            },
                        )
                        DropdownMenuItem(
                            text = { Text("登出", color = TextSecondary) },
                            onClick = {
                                menuExpanded = false
                                scope.launch { container.authRepository.logout() }
                            },
                        )
                    }
                },
            )
        },
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding)) {
            // 分類 Chip 列
            LazyRow(
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                item {
                    FilterChip("全部", selectedCategory == null) { selectedCategory = null }
                }
                items(categories) { cat ->
                    FilterChip(cat.name, selectedCategory == cat.id) {
                        selectedCategory = if (selectedCategory == cat.id) null else cat.id
                    }
                }
            }

            when {
                loading -> CenterBox { CircularProgressIndicator() }
                error != null -> CenterBox { Text(error!!, color = MaterialTheme.colorScheme.error) }
                dramas.isEmpty() -> CenterBox { Text("尚無劇集") }
                else -> LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    contentPadding = PaddingValues(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    items(dramas) { drama ->
                        DramaCard(drama = drama, onClick = { onOpenDrama(drama.id) })
                    }
                }
            }
        }
    }

    if (showAbout) {
        AlertDialog(
            onDismissRequest = { showAbout = false },
            title = { Text("關於") },
            text = { Text("版本 v${BuildConfig.VERSION_NAME}") },
            confirmButton = {
                TextButton(onClick = { showAbout = false }) { Text("關閉") }
            },
        )
    }
}

@Composable
private fun FilterChip(label: String, selected: Boolean, onClick: () -> Unit) {
    androidx.compose.material3.FilterChip(
        selected = selected,
        onClick = onClick,
        label = { Text(label) },
        colors = FilterChipDefaults.filterChipColors(
            containerColor = if (selected) Accent else SurfaceRaised,
            labelColor = if (selected) TextOnAccent else TextSecondary,
        ),
        border = androidx.compose.material3.FilterChipDefaults.filterChipBorder(
            enabled = true,
            selected = selected,
            borderColor = BorderDefault,
        ),
    )
}

/**
 * 海報式 DramaCard：封面 3:4 + 底部漸層 scrim + 頂左分類膠囊 + 2 行標題 + N 集。
 */
@Composable
private fun DramaCard(drama: Drama, onClick: () -> Unit) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = Surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp, pressedElevation = 8.dp),
    ) {
        Box {
            AsyncImage(
                model = drama.coverUrl ?: Constants.PLACEHOLDER_COVER,
                contentDescription = drama.title,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(3f / 4f),
            )
            // 底部漸層 scrim
            Box(
                Modifier
                    .fillMaxSize()
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(Color.Transparent, Color.Black.copy(alpha = 0.88f)),
                        )
                    )
            )
            // 頂左分類膠囊
            Box(
                modifier = Modifier
                    .align(Alignment.TopStart)
                    .padding(8.dp)
                    .clip(RoundedCornerShape(50))
                    .background(Color.Black.copy(alpha = 0.5f))
                    .padding(horizontal = 10.dp, vertical = 3.dp),
            ) {
                Text(
                    drama.categoryLabel,
                    style = MaterialTheme.typography.labelSmall,
                    color = TextPrimary,
                )
            }
            // 底部標題 + 集數
            Column(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(10.dp),
            ) {
                Text(
                    drama.title,
                    style = MaterialTheme.typography.titleSmall,
                    color = TextPrimary,
                    maxLines = 2,
                )
                drama.episodeCount?.let { n ->
                    androidx.compose.foundation.layout.Spacer(Modifier.height(4.dp))
                    Text(
                        "$n 集",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                    )
                }
            }
        }
    }
}

@Composable
private fun CenterBox(content: @Composable () -> Unit) {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { content() }
}
