
import os
import sys

# Add project root to sys.path for aux imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pathlib import Path
from typing import List, Union
from aux.validators.args_validation.decorators import validate

# -- Here starts
@validate
def validatePath(path: str, extension: Union[str, List[str]]) -> None | Exception:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not founded: {path}. Try again with other file.")
    if not path.is_file():
        raise TypeError(f"Given path is not a file: {path}. Try again with other file.")

    file_ext = path.suffix.lower().lstrip(".")

    if isinstance(extension, str):
        valid_exts = [extension.lower().lstrip(".")]
    elif isinstance(extension, list):
        valid_exts = [ext.lower().lstrip(".") for ext in extension]

    if file_ext not in valid_exts:
        raise ValueError(
            f"Invalid file extension: .{file_ext}. Expected: {valid_exts}"
        )

    return None