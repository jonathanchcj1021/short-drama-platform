package com.drama.app.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
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
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.drama.app.data.model.Category
import com.drama.app.data.model.Drama
import com.drama.app.di.AppContainer
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
                    Column {
                        Text("短劇平台")
                        container.authRepository.currentPhone?.let {
                            Text(it, style = MaterialTheme.typography.bodySmall)
                        }
                    }
                },
                actions = {
                    IconButton(onClick = { menuExpanded = true }) {
                        Icon(Icons.Default.MoreVert, contentDescription = "選單")
                    }
                    DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) {
                        DropdownMenuItem(
                            text = { Text("登出") },
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
}

@Composable
private fun FilterChip(label: String, selected: Boolean, onClick: () -> Unit) {
    androidx.compose.material3.FilterChip(
        selected = selected,
        onClick = onClick,
        label = { Text(label) },
    )
}

@Composable
private fun DramaCard(drama: Drama, onClick: () -> Unit) {
    Card(onClick = onClick, modifier = Modifier.fillMaxWidth()) {
        AsyncImage(
            model = drama.coverUrl ?: Constants.PLACEHOLDER_COVER,
            contentDescription = drama.title,
            contentScale = ContentScale.Crop,
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(2f / 3f),
        )
        Column(Modifier.padding(8.dp)) {
            Text(drama.title, style = MaterialTheme.typography.titleSmall, maxLines = 1)
            Text(
                drama.category?.name ?: "分類未設定",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun CenterBox(content: @Composable () -> Unit) {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { content() }
}
