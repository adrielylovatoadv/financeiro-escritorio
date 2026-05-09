[app]
title = L&E ADV
package.name = leadv
package.domain = com.leadv

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = data/*.json

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,android

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.arch = arm64-v8a

android.allow_backup = True

# Ícone do app (coloque le_adv_icon.png na pasta mobile/)
# android.icon.filename = %(source.dir)s/le_adv_icon.png

[buildozer]
log_level = 2
warn_on_root = 1
