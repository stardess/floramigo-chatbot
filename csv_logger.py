import csv
import os
from datetime import datetime
from typing import Dict, List


class CSVLogger:
	def __init__(self, csv_path: str, field_order: List[str]):
		self.csv_path = csv_path
		self.field_order = field_order
		self._ensure_header()

	def _ensure_header(self) -> None:
		file_exists = os.path.exists(self.csv_path)
		if not file_exists:
			with open(self.csv_path, mode="w", newline="") as f:
				writer = csv.writer(f)
				header = ["timestamp"] + self.field_order
				writer.writerow(header)

	def log(self, readings: Dict[str, float]) -> None:
		row = [datetime.utcnow().isoformat()]
		for key in self.field_order:
			row.append(readings.get(key))
		with open(self.csv_path, mode="a", newline="") as f:
			writer = csv.writer(f)
			writer.writerow(row)

import csv
import os
from datetime import datetime
from typing import Dict, List


class CSVLogger:
    def __init__(self, file_path: str, field_order: List[str]):
        self.file_path = file_path
        self.field_order = ["timestamp"] + field_order
        self._ensure_header()

    def _ensure_header(self) -> None:
        header_needed = not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0
        if header_needed:
            with open(self.file_path, mode="w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.field_order)
                writer.writeheader()

    def log(self, readings: Dict[str, float]) -> None:
        row = {key: "" for key in self.field_order}
        row["timestamp"] = datetime.utcnow().isoformat()
        for key, value in readings.items():
            if key in self.field_order:
                row[key] = value
        with open(self.file_path, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.field_order)
            writer.writerow(row)

