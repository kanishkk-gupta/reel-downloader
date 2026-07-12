"""
Reel Downloader - Kivy Mobile App
Simple paste-and-download Instagram Reel downloader for Android
"""

import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
import yt_dlp

# Android storage path
try:
    from android.storage import primary_external_storage_path
    DOWNLOAD_DIR = os.path.join(primary_external_storage_path(), "Reels")
except Exception:
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Reels")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex("#E1306C"))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])


class ReelDownloaderApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex("#0A0A0F")
        self.title = "Reel Downloader"

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))

        # ── Header ──
        header = Label(
            text="[b]📥 Reel Downloader[/b]",
            markup=True,
            font_size=dp(26),
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None,
            height=dp(60),
        )
        root.add_widget(header)

        subtitle = Label(
            text="Paste an Instagram Reel link below",
            font_size=dp(14),
            color=get_color_from_hex("#888899"),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(subtitle)

        # ── URL Input ──
        self.url_input = TextInput(
            hint_text="https://www.instagram.com/reel/...",
            multiline=False,
            font_size=dp(14),
            background_color=get_color_from_hex("#1A1A2E"),
            foreground_color=get_color_from_hex("#FFFFFF"),
            hint_text_color=get_color_from_hex("#555566"),
            cursor_color=get_color_from_hex("#E1306C"),
            padding=[dp(14), dp(12)],
            size_hint_y=None,
            height=dp(52),
        )
        root.add_widget(self.url_input)

        # ── Download Button ──
        self.download_btn = RoundedButton(
            text="⬇  Download Reel",
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex("#FFFFFF"),
            size_hint_y=None,
            height=dp(54),
        )
        self.download_btn.bind(on_press=self.start_download)
        root.add_widget(self.download_btn)

        # ── Progress Bar ──
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(8),
        )
        root.add_widget(self.progress)

        # ── Status Label ──
        self.status_label = Label(
            text="Ready",
            font_size=dp(13),
            color=get_color_from_hex("#888899"),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(self.status_label)

        # ── Log Area ──
        log_scroll = ScrollView(size_hint=(1, 1))
        self.log_label = Label(
            text="",
            font_size=dp(12),
            color=get_color_from_hex("#AAAACC"),
            markup=True,
            halign="left",
            valign="top",
            size_hint_y=None,
            text_size=(Window.width - dp(40), None),
        )
        self.log_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        log_scroll.add_widget(self.log_label)
        root.add_widget(log_scroll)

        # ── Save Path Label ──
        save_label = Label(
            text=f"[color=#555566]Saves to: {DOWNLOAD_DIR}[/color]",
            markup=True,
            font_size=dp(11),
            size_hint_y=None,
            height=dp(24),
        )
        root.add_widget(save_label)

        return root

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.set_status("⚠ Please paste a link first!", "#FFCC00")
            return
        self.download_btn.disabled = True
        self.progress.value = 0
        self.log_label.text = ""
        self.set_status("Starting download...", "#E1306C")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        def progress_hook(d):
            if d["status"] == "downloading":
                pct = d.get("_percent_str", "0%").strip().replace("%", "")
                try:
                    Clock.schedule_once(lambda dt: setattr(self.progress, "value", float(pct)))
                except Exception:
                    pass
                msg = f"Downloading... {d.get('_percent_str','').strip()} of {d.get('_total_bytes_str','?')}"
                Clock.schedule_once(lambda dt, m=msg: self.set_status(m, "#E1306C"))
            elif d["status"] == "finished":
                Clock.schedule_once(lambda dt: setattr(self.progress, "value", 100))

        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": False,
            "progress_hooks": [progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Reel")
                msg = f"[color=#44FF88]✅ Done![/color]\n[color=#AAAACC]{title}[/color]\n\nSaved to:\n{DOWNLOAD_DIR}"
                Clock.schedule_once(lambda dt: self._on_success(msg))
        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._on_error(err))

    def _on_success(self, msg):
        self.log_label.text = msg
        self.set_status("Download complete ✅", "#44FF88")
        self.download_btn.disabled = False
        self.url_input.text = ""

    def _on_error(self, err):
        self.log_label.text = f"[color=#FF4444]❌ Error:[/color]\n{err}"
        self.set_status("Download failed ❌", "#FF4444")
        self.download_btn.disabled = False

    def set_status(self, text, color_hex):
        self.status_label.text = text
        self.status_label.color = get_color_from_hex(color_hex)


if __name__ == "__main__":
    ReelDownloaderApp().run()