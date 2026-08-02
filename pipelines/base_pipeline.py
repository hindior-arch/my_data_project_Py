import json
from pathlib import Path
from datetime import datetime
import pandas as pd

from logging_config import setup_logger

logger = setup_logger()


class BasePipeline:
    def __init__(self, client, config, entity_name, per_page):
        self.client = client
        self.config = config
        self.entity_name = entity_name
        self.per_page = per_page
        self.raw_data = []
        self.cleaned_data = []

        self.raw_dir = Path(f"data/raw/{self.entity_name}")
        self.curated_dir = Path(f"data/curated/{self.entity_name}")
        self.state_dir = Path("data/state")

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.curated_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.state_dir / f"{self.entity_name}_last_run.json"

    def get_last_watermark(self):
        logger.info("Loading watermark | entity=%s | file=%s", self.entity_name, self.state_file)

        if not self.state_file.exists():
            logger.warning("Watermark file not found | entity=%s", self.entity_name)
            return None

        try:
            with open(self.state_file, "r", encoding="utf-8-sig") as f:
                content = f.read().strip()

            if not content:
                logger.warning("Watermark file is empty | entity=%s | file=%s", self.entity_name, self.state_file)
                return None

            state = json.loads(content)
            return state.get("last_modified")

        except json.JSONDecodeError:
            logger.warning("Invalid watermark JSON | entity=%s | file=%s", self.entity_name, self.state_file)
            return None

    def save_watermark(self, value):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump({"last_modified": value}, f, ensure_ascii=False, indent=2)

        logger.info("Watermark saved | entity=%s | value=%s", self.entity_name, value)

    def extract(self):
        raise NotImplementedError

    def transform(self):
        raise NotImplementedError

    def load(self):
        logger.info("Load started | entity=%s | rows=%s", self.entity_name, len(self.cleaned_data))

        df = pd.DataFrame(self.cleaned_data)

        if df.empty:
            logger.warning("No data to save | entity=%s", self.entity_name)
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        raw_dir = Path("data/raw") / self.entity_name
        curated_dir = Path("data/curated") / self.entity_name

        raw_dir.mkdir(parents=True, exist_ok=True)
        curated_dir.mkdir(parents=True, exist_ok=True)

        latest_csv = curated_dir / f"{self.entity_name}_latest.csv"
        save_raw_history = getattr(self, "save_raw_history", True)

        if save_raw_history:
            raw_csv = raw_dir / f"{self.entity_name}_{timestamp}.csv"
            df.to_csv(raw_csv, index=False, encoding="utf-8-sig")
            logger.info("Raw CSV saved | entity=%s | path=%s", self.entity_name, raw_csv)

        df.to_csv(latest_csv, index=False, encoding="utf-8-sig")
        logger.info("Latest CSV saved | entity=%s | path=%s", self.entity_name, latest_csv)