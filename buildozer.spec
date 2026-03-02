[app]

title = Video Downloader
package.name = videodownloader
package.domain = com.exapps
version = 1.0.0

orientation = portrait

requirements = python3,kivy,yt-dlp,androidstorage4kivy,plyer,Pillow

fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.accept_sdk_license = True

icon.filename = icon.png

source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,json
source.exclude_patterns = __pycache__,*.pyc,*.pyo,.git

log_level = 2
android.debug_port = 0
android.allow_backup = True

window.width = 480
window.height = 800
window.top = 0
window.left = 0

android.presplash_color = #1A1A2E

android.wakelock = True
android.copy_libs = 1

p4a.bootstrap = sdl2
