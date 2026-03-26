"Decorators for arg validation."
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from exceptions.validations.arg_validation_exceptions import WrongArgTypeError

def validate(func):
    wrapped = beartype(func)
    def wrapper(*args, **kwargs):
        try:
            return wrapped(*args, **kwargs)
        except BeartypeCallHintParamViolation as b:
            raise WrongArgTypeError(f'Arg type not allowed: {b}')
    return wrapper