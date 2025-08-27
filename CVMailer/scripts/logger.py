import csv
from pathlib import Path
from typing import Dict

def append_log(log_csv: Path, row: Dict):
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    file_exists = log_csv.exists()
    with log_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "timestamp", "company", "channel", "target", "status", "details"
        ])
        if not file_exists:
            w.writeheader()
        w.writerow(row)
