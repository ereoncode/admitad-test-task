import json
from pathlib import Path
from typing import List, Union, Optional

import settings
from etl.types import LogRecord


def extract_logs(logfile: Optional[Union[str, Path]] = None) -> List[LogRecord]:
    """Extract Ours service logs"""
    logfile = logfile or settings.LOG_FILE

    with open(logfile, 'r') as f:
        return json.load(f)
