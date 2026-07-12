[app]
title = Reel Downloader
package.name = reeldownloader
package.domain = com.maa.reels

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy==2.3.0,yt-dlp,certifi,charset-normalizer,idna,urllib3,requests,mutagen,pycryptodomex,websockets,brotli

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Build settings
android.archs = arm64-v8a
android.release_artifact = apk
android.debug = False

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
