import os
import io
import pandas as pd
from pathlib import Path
from logics.engine import Engine
from typing import Optional, Any
from logics.services.base_service import BaseService
from datetime import datetime, timezone, timedelta


class LoadingTradingService(BaseService):

    def __init__(self, engine: Engine, path: Path):
        super().__init__(engine)
        self.Path = path

    def get_data_frame(
            self,
            tf: str,
            period: int,
            column: Optional[str] = None,
            to_date: Optional[datetime] = None
    ) -> Any:
        candle_count = period * 5 if tf == "weekly" else period
        # Load the data frame
        df = self.load_symbol_history(period=candle_count, end_date=to_date)

        # Resample the data frame
        dct: dict = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }

        # Reformat the index from Datetime offset to Date
        df.index = df.index.map(lambda x: x.date())
        df.index = pd.to_datetime(df.index)

        if tf == "weekly":
            return df[column].resample("W").apply(dct[column])[-period:] \
                if column else df.resample("W").apply(dct)[-period:]
        return df[-period:] if column is None else df[column][-period:]

    def load_symbol_history(
            self,
            period=160,
            end_date: Optional[datetime] = None,
            chunk_size=1024 * 6
    ) -> pd.DataFrame | None:
        def get_date(start, chunk) -> datetime:
            end = chunk.find(b",", start)
            date_str = chunk[start:end].decode()

            if len(date_str) > 10:
                return datetime.strptime(date_str[:25], "%Y-%m-%d %H:%M:%S%z")
            else:
                return datetime.strptime(date_str, "%Y-%m-%d")

        size = os.path.getsize(self.Path)
        if end_date is not None:
            end_date = end_date.replace(tzinfo=timezone(timedelta(days=-1, seconds=72000)))

        if size <= chunk_size and not end_date:
            try:
                df = pd.read_csv(self.Path, index_col="Date", dtype={"Date": object})
                df.index = pd.to_datetime(df.index, utc=True)
                df.set_index(df.index, inplace=True)
                return df.iloc[-period:]
            except Exception as e:
                print(f"Error: {e}")
                return None

        chunks_read = []  # store the bytes chunk in a list
        start_date = None
        prev_chunk_start_line = None
        holiday_offset = max(3, period // 50 * 3)

        if end_date:
            start_date = end_date - pd.offsets.BDay(period + holiday_offset)

        # Open in binary mode and read from end of file
        with self.Path.open(mode="rb") as f:
            # Read the first line of file to get column names
            columns = f.readline()
            curr_pos = size

            while curr_pos > 0:
                read_size = min(chunk_size, curr_pos)
                # Set the current read position in the file
                f.seek(curr_pos - read_size)
                # From the current position read n bytes
                chunk = f.read(read_size)
                if end_date:
                    # The First line in a chunk may not be complete line
                    # So skip the first line and parse the first date in chunk
                    newline_index = chunk.find(b"\n")
                    start = newline_index + 1
                    current_dt = get_date(start, chunk)
                    # start storing chunks once end date has reached
                    if current_dt <= end_date:
                        if prev_chunk_start_line:
                            chunk = chunk + prev_chunk_start_line
                            prev_chunk_start_line = None
                        if start_date and current_dt <= start_date:
                            # reached starting date
                            # add the columns to chunk and append it
                            chunks_read.append(columns + chunk[start:])
                            break
                        chunks_read.append(chunk)
                    else:
                        prev_chunk_start_line = chunk[: chunk.find(b"\n")]
                else:
                    if curr_pos == size:
                        # On the first chunk, get the last date to calculate start_date
                        last_newline_index = chunk[:-1].rfind(b"\n")
                        start = last_newline_index + 1
                        last_dt = get_date(start, chunk)
                        start_date = last_dt - pd.offsets.BDay(period + holiday_offset)
                    # The First line may not be a complete line.
                    # To skip this line, find the first newline character
                    newline_index = chunk.find(b"\n")
                    start = newline_index + 1
                    try:
                        current_dt = get_date(start, chunk)
                    except ValueError:
                        # Reached start of the file. No valid date to parse
                        chunks_read.append(chunk)
                        break
                    if start_date is None:
                        start_date = datetime.now() - pd.offsets.BDay(period + holiday_offset)
                    if current_dt <= start_date:
                        # Concatenate the columns and chunk together
                        # and append to list
                        chunks_read.append(columns + chunk[start:])
                        break
                    # We are storing the chunks in bottom first order.
                    # This has to be corrected later by reversing the list
                    chunks_read.append(chunk)
                curr_pos -= read_size

            if end_date and not chunks_read:
                # If chunks_read is empty, end_date was not found in file
                raise IndexError("Date out of bounds of current DataFrame")

            # Reverse the list and join it into a bytes string.
            # Store the result in a buffer
            buffer = io.BytesIO(b"".join(chunks_read[::-1]))

        # Return result as DataFrame
        df = pd.read_csv(buffer, dtype={"Date": object})
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
        df.set_index("Date", inplace=True)
        return df.loc[:end_date].iloc[-period:] if end_date else df.iloc[-period:]


