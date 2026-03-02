#!/usr/bin/env python3
"""
🎬 Video Downloader Android App
Kivy-based application for downloading videos
"""

import os
import re
import threading
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock, mainthread
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

# For Android permissions
try:
    from android import mActivity
    from android.permissions import request_permissions, check_permission
    ANDROID = True
except ImportError:
    ANDROID = False

# Import downloader
import yt_dlp


# ==================== COLORS ====================
COLORS = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4',
    'dark': '#2C3E50',
    'light': '#ECF0F1',
    'success': '#27AE60',
    'error': '#E74C3C',
    'warning': '#F39C12',
    'background': '#1A1A2E',
    'surface': '#16213E',
    'text': '#FFFFFF',
    'text_secondary': '#A0A0A0',
}


# ==================== QUALITY & FORMAT ====================
QUALITY_OPTIONS = [
    'Best Quality',
    '1080p',
    '720p',
    '480p',
    '360p',
    'Audio Only',
]

FORMAT_OPTIONS = [
    'MP4 (Video)',
    'WebM (Video)',
    'MP3 (Audio)',
    'M4A (Audio)',
    'WAV (Audio)',
]

QUALITY_MAP = {
    'Best Quality': 'best',
    '1080p': 'best[height<=1080]',
    '720p': 'best[height<=720]',
    '480p': 'best[height<=480]',
    '360p': 'best[height<=360]',
    'Audio Only': 'bestaudio',
}

FORMAT_MAP = {
    'MP4 (Video)': ('mp4', False),
    'WebM (Video)': ('webm', False),
    'MP3 (Audio)': ('mp3', True),
    'M4A (Audio)': ('m4a', True),
    'WAV (Audio)': ('wav', True),
}


# ==================== DOWNLOADER CLASS ====================
class VideoDownloaderAndroid:
    """Video downloader for Android."""
    
    PLATFORM_PATTERNS = {
        'youtube': r'(?:youtube\.com|youtu\.be|youtube-nocookie\.com)',
        'tiktok': r'tiktok\.com',
        'twitter': r'(?:twitter\.com|x\.com)',
        'instagram': r'instagram\.com',
        'facebook': r'facebook\.com|fb\.watch',
        'vimeo': r'vimeo\.com',
        'twitch': r'twitch\.tv',
        'reddit': r'reddit\.com',
    }
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or '/storage/emulated/0/Download/VideoDownloader'
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.current_progress = 0
        self.current_speed = 0
        self.current_status = ''
        self.download_cancelled = False
    
    def get_platform(self, url):
        """Detect platform from URL."""
        for platform, pattern in self.PLATFORM_PATTERNS.items():
            if re.search(pattern, url, re.IGNORECASE):
                return platform
        return 'unknown'
    
    def get_ydl_opts(self, progress_callback=None):
        """Get yt-dlp options."""
        return {
            'format': 'best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'progress_hooks': [progress_callback] if progress_callback else [],
            'nocheckcertificate': True,
        }
    
    def progress_hook(self, d):
        """Progress hook."""
        if self.download_cancelled:
            raise Exception('Download cancelled')
        
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                self.current_progress = (downloaded / total) * 100
            speed = d.get('speed', 0)
            if speed:
                self.current_speed = speed / 1024 / 1024  # MB/s
        
        elif d['status'] == 'finished':
            self.current_progress = 100
    
    def download(self, url, quality='best', output_format='mp4', audio_only=False):
        """Download video."""
        self.download_cancelled = False
        self.current_progress = 0
        self.current_speed = 0
        
        ydl_opts = self.get_ydl_opts(progress_callback=self.progress_hook)
        
        # Set format
        if audio_only or output_format in ['mp3', 'm4a', 'wav']:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format if output_format in ['mp3', 'm4a', 'wav'] else 'mp3',
            }]
            ydl_opts['format'] = 'bestaudio'
        else:
            if quality != 'best':
                ydl_opts['format'] = f'best[height<={quality.replace("p","")}]'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'success': True,
                    'title': info.get('title'),
                    'filename': ydl.prepare_filename(info),
                    'platform': self.get_platform(url),
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_info(self, url):
        """Get video info without downloading."""
        ydl_opts = self.get_ydl_opts()
        ydl_opts['skip_download'] = True
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            return None
    
    def cancel(self):
        """Cancel current download."""
        self.download_cancelled = True


# ==================== KIVY WIDGETS ====================

class StyledButton(Button):
    """Custom styled button."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(COLORS['primary'])
        self.color = get_color_from_hex(COLORS['text'])
        self.font_size = '16sp'
        self.size_hint_y = None
        self.height = '50dp'


class StyledTextInput(TextInput):
    """Custom styled text input."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex(COLORS['surface'])
        self.foreground_color = get_color_from_hex(COLORS['text'])
        self.cursor_color = get_color_from_hex(COLORS['primary'])
        self.padding = ['10dp', '10dp', '10dp', '10dp']


class DownloadItem(BoxLayout):
    """Download item widget."""
    status = StringProperty('')
    progress = NumericProperty(0)
    
    def __init__(self, url, title='', **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.title = title or url[:30] + '...'
        self.status = 'Waiting'


# ==================== MAIN SCREEN ====================
class MainScreen(Screen):
    """Main screen of the app."""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.downloader = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main layout
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        
        # Header
        header = BoxLayout(size_hint_y=None, height='60dp')
        header.add_widget(Label(
            text='🎬 Video Downloader',
            font_size='22sp',
            color=get_color_from_hex(COLORS['text']),
            halign='center'
        ))
        layout.add_widget(header)
        
        # URL Input
        url_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp')
        url_layout.add_widget(Label(
            text='🔗 Paste URL here:',
            size_hint_y=None,
            height='30dp',
            color=get_color_from_hex(COLORS['text_secondary'])
        ))
        
        self.url_input = StyledTextInput(
            multiline=False,
            hint_text='https://youtube.com/watch?v=...',
            size_hint_y=None,
            height='60dp'
        )
        url_layout.add_widget(self.url_input)
        
        # Quick paste button
        paste_btn = StyledButton(
            text='📋 Paste from Clipboard',
            size_hint_y=None,
            height='40dp',
            background_color=get_color_from_hex(COLORS['secondary'])
        )
        paste_btn.bind(on_press=self.paste_from_clipboard)
        url_layout.add_widget(paste_btn)
        
        layout.add_widget(url_layout)
        
        # Quality & Format Selection
        settings_layout = GridLayout(cols=2, size_hint_y=None, height='120dp', spacing='10dp')
        
        # Quality spinner
        settings_layout.add_widget(Label(
            text='📊 Quality:',
            color=get_color_from_hex(COLORS['text_secondary'])
        ))
        self.quality_spinner = Spinner(
            text='Best Quality',
            values=QUALITY_OPTIONS,
            background_color=get_color_from_hex(COLORS['surface']),
            color=get_color_from_hex(COLORS['text'])
        )
        settings_layout.add_widget(self.quality_spinner)
        
        # Format spinner
        settings_layout.add_widget(Label(
            text='📦 Format:',
            color=get_color_from_hex(COLORS['text_secondary'])
        ))
        self.format_spinner = Spinner(
            text='MP4 (Video)',
            values=FORMAT_OPTIONS,
            background_color=get_color_from_hex(COLORS['surface']),
            color=get_color_from_hex(COLORS['text'])
        )
        settings_layout.add_widget(self.format_spinner)
        
        layout.add_widget(settings_layout)
        
        # Options
        options_layout = GridLayout(cols=2, size_hint_y=None, height='80dp', spacing='10dp')
        
        # Subtitles checkbox
        self.subtitles_check = BoxLayout(size_hint_y=None, height='30dp')
        self.subtitles_check.add_widget(Label(text='📝 Subtitles', color=get_color_from_hex(COLORS['text_secondary'])))
        self.subtitles_cb = CheckBox(active=False, color=get_color_from_hex(COLORS['primary']))
        self.subtitles_check.add_widget(self.subtitles_cb)
        options_layout.add_widget(self.subtitles_check)
        
        # Thumbnail checkbox
        self.thumbnail_check = BoxLayout(size_hint_y=None, height='30dp')
        self.thumbnail_check.add_widget(Label(text='🖼️ Thumbnail', color=get_color_from_hex(COLORS['text_secondary'])))
        self.thumbnail_cb = CheckBox(active=False, color=get_color_from_hex(COLORS['primary']))
        self.thumbnail_check.add_widget(self.thumbnail_cb)
        options_layout.add_widget(self.thumbnail_check)
        
        layout.add_widget(options_layout)
        
        # Download button
        self.download_btn = StyledButton(
            text='⬇️ Start Download',
            background_color=get_color_from_hex(COLORS['success']),
            size_hint_y=None,
            height='60dp'
        )
        self.download_btn.bind(on_press=self.start_download)
        layout.add_widget(self.download_btn)
        
        # Progress section
        self.progress_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp')
        self.progress_layout.opacity = 0
        
        self.progress_label = Label(
            text='Downloading...',
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height='30dp'
        )
        self.progress_layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, value=0, height='30dp')
        self.progress_bar.background_color = get_color_from_hex(COLORS['surface'])
        self.progress_bar.color = get_color_from_hex(COLORS['primary'])
        self.progress_layout.add_widget(self.progress_bar)
        
        self.speed_label = Label(
            text='',
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height='20dp'
        )
        self.progress_layout.add_widget(self.speed_label)
        
        layout.add_widget(self.progress_layout)
        
        # Cancel button
        self.cancel_btn = StyledButton(
            text='❌ Cancel',
            background_color=get_color_from_hex(COLORS['error']),
            size_hint_y=None,
            height='50dp',
            opacity=0
        )
        self.cancel_btn.bind(on_press=self.cancel_download)
        layout.add_widget(self.cancel_btn)
        
        # Info button
        info_btn = StyledButton(
            text='ℹ️ Get Video Info',
            background_color=get_color_from_hex(COLORS['warning']),
            size_hint_y=None,
            height='45dp'
        )
        info_btn.bind(on_press=self.get_video_info)
        layout.add_widget(info_btn)
        
        # Output directory
        output_layout = BoxLayout(size_hint_y=None, height='40dp')
        output_layout.add_widget(Label(
            text='📁 Output: /storage/emulated/0/Download/VideoDownloader',
            color=get_color_from_hex(COLORS['text_secondary']),
            font_size='12sp'
        ))
        layout.add_widget(output_layout)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height='30dp'
        )
        layout.add_widget(self.status_label)
        
        # Add scroll view
        scroll = ScrollView()
        scroll.add_widget(layout)
        self.add_widget(scroll)
    
    def paste_from_clipboard(self, *args):
        """Paste from clipboard."""
        try:
            from kivy.core.clipboard import Clipboard
            clipboard_text = Clipboard.paste()
            if clipboard_text:
                self.url_input.text = clipboard_text
                self.status_label.text = '✓ Pasted from clipboard'
        except:
            self.status_label.text = '📋 Tap URL field to paste'
    
    def start_download(self, *args):
        """Start download."""
        url = self.url_input.text.strip()
        
        if not url:
            self.status_label.text = '⚠️ Please enter a URL'
            return
        
        # Validate URL
        if not re.match(r'https?://', url):
            url = 'https://' + url
            self.url_input.text = url
        
        # Get quality and format
        quality = QUALITY_MAP.get(self.quality_spinner.text, 'best')
        format_text = self.format_spinner.text
        output_format, audio_only = FORMAT_MAP.get(format_text, ('mp4', False))
        
        # Show progress
        self.progress_layout.opacity = 1
        self.cancel_btn.opacity = 1
        self.download_btn.disabled = True
        self.status_label.text = '⏳ Starting download...'
        
        # Create downloader
        self.downloader = VideoDownloaderAndroid()
        
        # Start download in thread
        threading.Thread(target=self._download_thread, args=(url, quality, output_format, audio_only)).start()
    
    def _download_thread(self, url, quality, output_format, audio_only):
        """Download thread."""
        try:
            result = self.downloader.download(url, quality, output_format, audio_only)
            
            Clock.schedule_once(lambda dt: self._download_complete(result))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._download_error(str(e)))
    
    @mainthread
    def _download_complete(self, result):
        """Handle download complete."""
        self.progress_layout.opacity = 0
        self.cancel_btn.opacity = 0
        self.download_btn.disabled = False
        
        if result.get('success'):
            self.status_label.text = f'✓ Download complete!'
            self.show_popup('Success', f'✅ Downloaded: {result.get("title", "Unknown")}')
        else:
            self.status_label.text = f'❌ Download failed'
            self.show_popup('Error', f'❌ {result.get("error", "Unknown error")}')
    
    @mainthread
    def _download_error(self, error):
        """Handle download error."""
        self.progress_layout.opacity = 0
        self.cancel_btn.opacity = 0
        self.download_btn.disabled = False
        self.status_label.text = f'❌ Error: {error}'
        self.show_popup('Error', f'❌ {error}')
    
    def cancel_download(self, *args):
        """Cancel download."""
        if self.downloader:
            self.downloader.cancel()
            self.status_label.text = '❌ Download cancelled'
        
        self.progress_layout.opacity = 0
        self.cancel_btn.opacity = 0
        self.download_btn.disabled = False
    
    def get_video_info(self, *args):
        """Get video info."""
        url = self.url_input.text.strip()
        
        if not url:
            self.status_label.text = '⚠️ Please enter a URL'
            return
        
        self.status_label.text = '⏳ Fetching info...'
        
        def fetch_info():
            try:
                downloader = VideoDownloaderAndroid()
                info = downloader.get_info(url)
                
                if info:
                    Clock.schedule_once(lambda dt: self._show_info(info))
                else:
                    Clock.schedule_once(lambda dt: self.status_label.text)
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.status_label.text)
        
        threading.Thread(target=fetch_info).start()
    
    @mainthread
    def _show_info(self, info):
        """Show video info."""
        title = info.get('title', 'Unknown')
        duration = info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        views = info.get('view_count', 0)
        uploader = info.get('uploader', 'Unknown')
        
        info_text = f"""
📌 Title: {title}
⏱️ Duration: {minutes}:{seconds:02d}
👁️ Views: {views:,}
👤 Uploader: {uploader}
"""
        self.status_label.text = 'ℹ️ Info loaded'
        self.show_popup('Video Info', info_text)
    
    def show_popup(self, title, content):
        """Show popup."""
        popup = Popup(
            title=title,
            content=Label(text=content, text_size=(None, None), halign='center'),
            size_hint=(0.9, 0.6),
            background_color=get_color_from_hex(COLORS['surface'])
        )
        popup.open()


# ==================== APP CLASS ====================
class VideoDownloaderApp(App):
    """Main application class."""
    
    def build(self):
        """Build the app."""
        # Request permissions
        self.request_permissions()
        
        # Set background color
        Window.clearcolor = get_color_from_hex(COLORS['background'])
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(MainScreen(self, name='main'))
        
        return sm
    
    def request_permissions(self):
        """Request Android permissions."""
        if ANDROID:
            permissions = [
                'android.permission.INTERNET',
                'android.permission.READ_EXTERNAL_STORAGE',
                'android.permission.WRITE_EXTERNAL_STORAGE',
                'android.permission.ACCESS_NETWORK_STATE',
            ]
            try:
                request_permissions(permissions)
            except:
                pass
    
    def on_pause(self):
        """Handle pause."""
        return True
    
    def on_resume(self):
        """Handle resume."""
        pass


# ==================== MAIN ====================
if __name__ == '__main__':
    VideoDownloaderApp().run()
