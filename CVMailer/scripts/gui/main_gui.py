from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
import threading
from scripts.config_loader import load_or_init_config
from scripts.companies import read_companies
from scripts.processor import process_company
from scripts.utils import random_delay
from pathlib import Path


class MainTab(MDBoxLayout, MDTabsBase):
    """Main tab with progress, start button, and logs"""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=15, padding=20, **kwargs)
        self.title = "Dashboard"  # 🔥 нужно для MDTab

        self.status_label = MDLabel(text="Ready", halign="center", theme_text_color="Primary")
        self.progress_bar = MDProgressBar(value=0)
        self.logs_output = MDTextField(multiline=True, readonly=True, hint_text="Logs will appear here")
        self.start_btn = MDRaisedButton(
            text="Start Sending",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.start_sending()
        )

        self.add_widget(self.status_label)
        self.add_widget(self.progress_bar)
        self.add_widget(self.logs_output)
        self.add_widget(self.start_btn)

    # ----------- Logic -----------
    def start_sending(self):
        self.status_label.text = "Starting..."
        self.logs_output.text = ""
        threading.Thread(target=self.run_mailing).start()

    def run_mailing(self):
        cfg = load_or_init_config(Path("./config/config.yaml"))
        companies = read_companies(Path("./companies.csv"))
        total = len(companies)
        count = 0

        for comp in companies:
            if not comp.company:
                continue
            if not comp.contact_email and not comp.apply_url:
                self.append_log(f"[!] Skipping {comp.company}: no contact_email or apply_url")
                continue

            self.append_log(f"[*] Processing {comp.company} ...")
            process_company(cfg, comp, dry_run=False, mode="both")
            count += 1

            progress = int((count / total) * 100)
            min_delay = cfg.get("forms", {}).get("min_delay_s", 5)
            max_delay = cfg.get("forms", {}).get("max_delay_s", 15)
            random_delay(min_delay, max_delay)

            self.update_status(f"Processed {count}/{total}: {comp.company}", progress)

        self.update_status(f"Done! Processed {count} companies.", 100)
        self.append_log("[i] Done!")

    def update_status(self, text, progress=0):
        Clock.schedule_once(lambda dt: setattr(self.status_label, "text", text))
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, "value", progress))

    def append_log(self, message: str):
        def _update(dt):
            self.logs_output.text += message + "\n"
        Clock.schedule_once(_update)
