"Decorators for arg validation."
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation

import os
import sys
# Add project root to sys.path for aux imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from exceptions.validations.arg_validation_exceptions import WrongArgTypeError

def validate(func):
    wrapped = beartype(func)
    def wrapper(*args, **kwargs):
        try:
            return wrapped(*args, **kwargs)
        except BeartypeCallHintParamViolation as b:
            raise WrongArgTypeError(f'Arg type not allowed: {b}')
    return wrapper