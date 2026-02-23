from __future__ import annotations

import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:

    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename

        self._acc_f = None
        self._gps_f = None
        self._acc_reader: Optional[csv.reader] = None
        self._gps_reader: Optional[csv.reader] = None

        self._started = False

        # one-row buffers (supports CSVs with or without header)
        self._acc_buf: Optional[List[str]] = None
        self._gps_buf: Optional[List[str]] = None

        self._acc_has_header: Optional[bool] = None
        self._gps_has_header: Optional[bool] = None

    def startReading(self, *args, **kwargs):
        """Must be called before read()"""
        if self._started:
            return

        if not Path(self.accelerometer_filename).exists():
            raise FileNotFoundError(f"Accelerometer file not found: {self.accelerometer_filename}")
        if not Path(self.gps_filename).exists():
            raise FileNotFoundError(f"GPS file not found: {self.gps_filename}")

        self._open_files()
        self._started = True

    def stopReading(self, *args, **kwargs):
        """Must be called when finishing reading"""
        self._close_files()
        self._started = False

    def read(self) -> AggregatedData:
        """Return one combined sample (acc + gps)."""
        if not self._started:
            raise RuntimeError("Datasource is not started. Call startReading() before read().")

        acc_row = self._next_acc_row()
        gps_row = self._next_gps_row()

        acc = self._parse_acc(acc_row)
        gps = self._parse_gps(gps_row)

        # IMPORTANT: timing belongs to datasource (not MQTT / main.py)
        if config.DELAY and config.DELAY > 0:
            time.sleep(float(config.DELAY))

        return AggregatedData(
            accelerometer=acc,
            gps=gps,
            time=datetime.utcnow(),
            user_id=config.USER_ID,
        )

    # ---------------- internal ----------------

    def _open_files(self) -> None:
        self._close_files()

        self._acc_f = open(self.accelerometer_filename, "r", newline="", encoding="utf-8")
        self._gps_f = open(self.gps_filename, "r", newline="", encoding="utf-8")

        self._acc_reader = csv.reader(self._acc_f)
        self._gps_reader = csv.reader(self._gps_f)

        self._acc_buf = None
        self._gps_buf = None

        self._acc_has_header, self._acc_buf = self._detect_header_and_buffer(
            self._acc_reader, expected_cols=3, header_tokens=("x", "y", "z")
        )
        self._gps_has_header, self._gps_buf = self._detect_header_and_buffer(
            self._gps_reader, expected_cols=2, header_tokens=("longitude", "latitude")
        )

    def _close_files(self) -> None:
        for f in (self._acc_f, self._gps_f):
            try:
                if f is not None:
                    f.close()
            except Exception:
                pass

        self._acc_f = None
        self._gps_f = None
        self._acc_reader = None
        self._gps_reader = None
        self._acc_buf = None
        self._gps_buf = None
        self._acc_has_header = None
        self._gps_has_header = None

    def _rewind_acc(self) -> None:
        if self._acc_f is None:
            raise RuntimeError("Accelerometer file is not open.")
        self._acc_f.seek(0)
        self._acc_reader = csv.reader(self._acc_f)
        self._acc_has_header, self._acc_buf = self._detect_header_and_buffer(
            self._acc_reader, expected_cols=3, header_tokens=("x", "y", "z")
        )

    def _rewind_gps(self) -> None:
        if self._gps_f is None:
            raise RuntimeError("GPS file is not open.")
        self._gps_f.seek(0)
        self._gps_reader = csv.reader(self._gps_f)
        self._gps_has_header, self._gps_buf = self._detect_header_and_buffer(
            self._gps_reader, expected_cols=2, header_tokens=("longitude", "latitude")
        )

    def _next_acc_row(self) -> List[str]:
        if self._acc_reader is None:
            raise RuntimeError("Accelerometer reader is not initialized.")

        while True:
            if self._acc_buf is not None:
                row = self._acc_buf
                self._acc_buf = None
            else:
                row = next(self._acc_reader, None)

            if row is None:
                # EOF -> rewind & continue
                self._rewind_acc()
                continue

            row = [c.strip() for c in row]
            if not row or not any(row):
                continue

            return row

    def _next_gps_row(self) -> List[str]:
        if self._gps_reader is None:
            raise RuntimeError("GPS reader is not initialized.")

        while True:
            if self._gps_buf is not None:
                row = self._gps_buf
                self._gps_buf = None
            else:
                row = next(self._gps_reader, None)

            if row is None:
                # EOF -> rewind & continue
                self._rewind_gps()
                continue

            row = [c.strip() for c in row]
            if not row or not any(row):
                continue

            return row

    @staticmethod
    def _detect_header_and_buffer(
        rdr: csv.reader, expected_cols: int, header_tokens: tuple[str, ...]
    ) -> tuple[bool, Optional[List[str]]]:

        first = None
        while True:
            first = next(rdr, None)
            if first is None:
                return False, None
            first = [c.strip() for c in first]
            if first and any(first):
                break

        norm = [c.lower() for c in first]

        # Header if it contains the expected tokens
        if all(tok in norm for tok in header_tokens):
            return True, None

        # If first row is numeric-like and has enough columns => it's data (buffer it back)
        if len(norm) >= expected_cols and all(FileDatasource._is_number(x) for x in norm[:expected_cols]):
            return False, first

        # Otherwise treat it as header-ish (skip it)
        return True, None

    @staticmethod
    def _parse_acc(row: List[str]) -> Accelerometer:
        if len(row) < 3:
            raise ValueError(f"Accelerometer row must have 3 values (x,y,z). Got: {row}")
        x = int(float(row[0]))
        y = int(float(row[1]))
        z = int(float(row[2]))
        return Accelerometer(x=x, y=y, z=z)

    @staticmethod
    def _parse_gps(row: List[str]) -> Gps:
        if len(row) < 2:
            raise ValueError(f"GPS row must have 2 values (longitude,latitude). Got: {row}")
        lon = float(row[0])
        lat = float(row[1])
        return Gps(longitude=lon, latitude=lat)

    @staticmethod
    def _is_number(s: str) -> bool:
        try:
            float(s)
            return True
        except Exception:
            return False