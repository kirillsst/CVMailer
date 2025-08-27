import csv
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class Company:
    company: str
    contact_email: Optional[str]
    apply_url: Optional[str]
    contact_name: Optional[str]
    intro_note: Optional[str]

def read_companies(csv_path: Path) -> List[Company]:
    if not csv_path.exists():
        # Create a starter CSV
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["company", "contact_email", "apply_url", "contact_name", "intro_note"])
            w.writerow(["Exemple SA", "hr@exemple.fr", "", "Mme Dupont", "project data/JS"])
            w.writerow(["Startup XYZ", "", "https://startup.xyz/jobs/stage-dev", "", "responsive web applications"])
        print(f"[i] Created template companies CSV at {csv_path}. Add your targets and rerun.")
    df = pd.read_csv(csv_path).fillna("")
    companies: List[Company] = []
    for _, row in df.iterrows():
        companies.append(Company(
            company=row.get("company", "").strip(),
            contact_email=row.get("contact_email", "").strip() or None,
            apply_url=row.get("apply_url", "").strip() or None,
            contact_name=row.get("contact_name", "").strip() or None,
            intro_note=row.get("intro_note", "").strip() or None,
        ))
    return companies
