package com.drama.app.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.drama.app.di.AppContainer
import com.drama.app.ui.detail.DramaDetailScreen
import com.drama.app.ui.home.HomeScreen
import com.drama.app.ui.login.LoginScreen
import com.drama.app.ui.play.PlayScreen
import kotlinx.coroutines.flow.collect

/** 導航路由定義。 */
object Routes {
    const val LOGIN = "login"
    const val HOME = "home"
    const val DETAIL = "detail/{dramaId}"
    const val PLAY = "play/{episodeId}/{dramaId}"

    fun detail(dramaId: Int) = "detail/$dramaId"
    fun play(episodeId: Int, dramaId: Int) = "play/$episodeId/$dramaId"
}

@Composable
fun AppNavGraph(container: AppContainer) {
    val navController = rememberNavController()

    // 收到 401：清空堆疊導回登入頁。
    LaunchedEffect(Unit) {
        container.tokenManager.unauthorizedEvents.collect {
            navController.navigate(Routes.LOGIN) {
                popUpTo(0) { inclusive = true }
            }
        }
    }

    val startDestination =
        if (container.authRepository.isLoggedIn) Routes.HOME else Routes.LOGIN

    NavHost(navController = navController, startDestination = startDestination) {

        composable(Routes.LOGIN) {
            LoginScreen(
                container = container,
                onLoggedIn = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                },
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                container = container,
                onOpenDrama = { dramaId -> navController.navigate(Routes.detail(dramaId)) },
            )
        }

        composable(
            route = Routes.DETAIL,
            arguments = listOf(navArgument("dramaId") { type = NavType.IntType }),
        ) { backStackEntry ->
            val dramaId = backStackEntry.arguments?.getInt("dramaId") ?: return@composable
            DramaDetailScreen(
                container = container,
                dramaId = dramaId,
                onBack = { navController.popBackStack() },
                onPlayEpisode = { episodeId ->
                    navController.navigate(Routes.play(episodeId, dramaId))
                },
            )
        }

        composable(
            route = Routes.PLAY,
            arguments = listOf(
                navArgument("episodeId") { type = NavType.IntType },
                navArgument("dramaId") { type = NavType.IntType },
            ),
        ) { backStackEntry ->
            val episodeId = backStackEntry.arguments?.getInt("episodeId") ?: return@composable
            val dramaId = backStackEntry.arguments?.getInt("dramaId") ?: return@composable
            PlayScreen(
                container = container,
                episodeId = episodeId,
                dramaId = dramaId,
                onBack = { navController.popBackStack() },
                onSwitchEpisode = { newEpisodeId ->
                    // 取代目前播放頁，避免堆疊爆炸
                    navController.navigate(Routes.play(newEpisodeId, dramaId)) {
                        popUpTo(Routes.PLAY) { inclusive = true }
                    }
                },
            )
        }
    }
}
