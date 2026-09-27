package com.drama.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.drama.app.ui.theme.ShortDramaTheme
import com.drama.app.navigation.AppNavGraph

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as DramaApp
        setContent {
            ShortDramaTheme {
                AppNavGraph(container = app.container)
            }
        }
    }
}
