from pathlib import Path
from typing import List
from aux.validators.args_validation.decorators import validate

# -- Here starts
@validate
def validatePath(path: str, extension: str | List[str]) -> True | Exception:
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}. Try again with another file.")    
    if not path.is_file():
        raise TypeError(f"Given path is not a file: {path}. Try again with another file.")

    if isinstance(extension, str):
        extensions = [extension]
    else:
        extensions = extension

    normalized_exts = []
    for ext in extensions:
        ext = ext.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
 
    file_ext = path.suffix.lower()

    if file_ext not in normalized_exts:
        raise ValueError(
            f"Invalid file extension: {file_ext}. "
            f"Expected: {normalized_exts}"
        )

    return True