import tempfile
import unittest
from pathlib import Path

import pandas as pd

from app.ingestion.linkedin_loader import (
    linkedin_data_to_text_chunks,
    load_linkedin_export,
)


class LinkedInIngestionTests(unittest.TestCase):
    def test_load_linkedin_export_and_build_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir)
            pd.DataFrame(
                [
                    {
                        "First Name": "Valentin",
                        "Last Name": "Milliet",
                        "Headline": "Data Scientist",
                        "Summary": "Profil orienté data et MLOps.",
                        "Location": "Paris",
                    }
                ]
            ).to_csv(raw_dir / "Profile.csv", index=False)
            pd.DataFrame(
                [
                    {
                        "Title": "Data Scientist",
                        "Company Name": "ACME",
                        "Description": "Construction de pipelines ML.",
                        "Started On": "2024",
                    }
                ]
            ).to_csv(raw_dir / "Positions.csv", index=False)
            pd.DataFrame([{"Name": "Python"}, {"Name": "FastAPI"}]).to_csv(
                raw_dir / "Skills.csv", index=False
            )

            data = load_linkedin_export(raw_dir)
            chunks = linkedin_data_to_text_chunks(data)

        self.assertEqual(data.profile.first_name, "Valentin")
        self.assertEqual(len(data.positions), 1)
        self.assertIn("Python", "\n".join(chunks))
        self.assertIn("Construction de pipelines ML.", "\n".join(chunks))
