from pathlib import Path
from typing import List
from aux.validators.decorators.args_validation import validate

# -- Here starts
@validate
def validatePath(path: str, extension: str | List[str]) -> True | Exception:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not founded: {path}. Try again with other file.")
    if not path.is_file():
        raise TypeError(f"Given path is not a file: {path}. Try again with other file.")
    return True