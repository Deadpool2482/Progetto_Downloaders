import os
import threading
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import mainthread
from kivy.properties import StringProperty

# Importa yt-dlp per scaricare i video
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

KV = '''
MDScreen:
    md_bg_color: 0.1, 0.1, 0.1, 1
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "20dp"
        pos_hint: {"center_x": .5, "center_y": .5}

        MDLabel:
            text: "UNIVERSAL DOWNLOADER"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 0, 1, 0, 1
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: url_input
            hint_text: "Incolla qui il link del video..."
            helper_text: "YouTube, Facebook, TikTok, ecc."
            helper_text_mode: "on_focus"
            icon_right: "link"
            icon_right_color: 1, 1, 1, 1
            multiline: False
            mode: "rectangle"
            line_color_normal: 1, 1, 1, 1
            line_color_focus: 0, 1, 0, 1
            text_color_normal: 1, 1, 1, 1
            text_color_focus: 1, 1, 1, 1

        MDFillRoundFlatButton:
            text: "SCARICA VIDEO"
            font_size: "18sp"
            size_hint_x: 1
            md_bg_color: 0, 0.7, 0, 1
            on_release: app.start_download()

        MDLabel:
            text: app.status_text
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 0.7
            font_style: "Body1"
'''

class DownloaderApp(MDApp):
    status_text = StringProperty("In attesa...")

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        return Builder.load_string(KV)

    def on_start(self):
        self.request_permissions()

    def request_permissions(self):
        # Richiede i permessi di scrittura su Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

    def start_download(self):
        url = self.root.ids.url_input.text
        if not url:
            self.status_text = "Errore: Inserisci un link!"
            return
        
        self.status_text = "Avvio download..."
        # Avvia il download in un thread separato per non bloccare l'app
        threading.Thread(target=self.download_logic, args=(url,)).start()

    def download_logic(self, url):
        # Configurazione cartella di salvataggio
        save_path = "Download" # Default per PC
        if platform == 'android':
            from android.storage import primary_external_storage_path
            save_path = os.path.join(primary_external_storage_path(), 'Download')

        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'format': 'best', # Scarica la migliore qualità disponibile (file singolo)
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video')
                
                self.update_status(f"Scaricando: {video_title[:20]}...")
                ydl.download([url])
                
                self.update_status("Download Completato! Controlla la Galleria.")
                self.clear_input()
        except Exception as e:
            self.update_status(f"Errore: {str(e)[:50]}")

    @mainthread
    def update_status(self, text):
        self.status_text = text

    @mainthread
    def clear_input(self):
        self.root.ids.url_input.text = ""

if __name__ == '__main__':
    DownloaderApp().run()