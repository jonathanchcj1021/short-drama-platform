package com.drama.app

import android.app.Application
import com.drama.app.di.AppContainer

class DramaApp : Application() {

    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
