# 🎬 Video Downloader Android App

A powerful video downloader app for Android built with Kivy.

## 📱 Features

### Supported Platforms
- 📺 YouTube / YouTube Music
- 🎵 TikTok
- 🐦 Twitter / X
- 📷 Instagram
- 📘 Facebook
- 🎬 Vimeo
- 🎮 Twitch
- 🤖 Reddit
- And many more...

### Download Options
- **Quality**: Best, 1080p, 720p, 480p, 360p, Audio Only
- **Format**: MP4, WebM, MP3, M4A, WAV
- **Subtitles**: Download subtitles in multiple languages
- **Thumbnail**: Extract video thumbnail

### Additional Features
- 🎯 Simple and intuitive interface
- 📋 Clipboard paste support
- ⏳ Progress tracking
- ❌ Cancel downloads
- ℹ️ Video information preview

## 📦 Installation

### Method 1: Pre-built APK
Download the latest APK from GitHub Releases.

### Method 2: Build from Source

#### Prerequisites
- Python 3.8+
- Java JDK 17
- Android SDK
- Linux (recommended) or macOS

#### Build Steps

1. **Install dependencies:**
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk wget unzip libssl-dev cmake autoconf automake zlib1g-dev libpng-dev

# Install Python dependencies
pip install buildozer kivy yt-dlp pillow plyer
```

2. **Build the APK:**
```bash
# Clone or download this project
cd videodl_android

# Build debug APK
buildozer android debug

# The APK will be in bin/ folder
```

3. **Install on device:**
```bash
adb install bin/videodl-1.0.0-armeabi-v7a-debug.apk
```

## 📂 Project Structure

```
videodl_android/
├── main.py              # Main Kivy application
├── buildozer.spec      # Build configuration
├── requirements.txt    # Python dependencies
├── icon.png           # App icon
├── README.md          # This file
└── .github/
    └── workflows/
        └── build.yml  # GitHub Actions workflow
```

## 🔧 GitHub Actions

The project includes automatic build workflow that:
1. Builds the APK on every push
2. Uploads the APK as an artifact
3. Creates a GitHub Release on main branch push

### Manual Build Trigger
Go to Actions tab → Build Android APK → Run workflow

## 📱 Permissions

The app requires the following permissions:
- `INTERNET` - For downloading videos
- `READ_EXTERNAL_STORAGE` - For reading downloaded files
- `WRITE_EXTERNAL_STORAGE` - For saving videos
- `ACCESS_NETWORK_STATE` - For checking network status

## 🛠️ Technology Stack

- **Framework**: Kivy 2.3.0
- **Download Engine**: yt-dlp
- **Build Tool**: Buildozer
- **Language**: Python 3.8+

## 📝 License

MIT License

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading engine
- [Kivy](https://kivy.org/) - Cross-platform Python framework
- [Buildozer](https://github.com/kivy/buildozer) - Build tool for mobile apps
