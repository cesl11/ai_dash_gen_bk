"Basic exceptions"

# --- Tools arg validations
class WrongArgTypeError(Exception):
    ...

class UnmatchingLabelAndDataArraySize(Exception):
    ...
    
# --- Chart errors
class UnknownChartType(Exception):
    ...
    
# --- Data source errors
class UnknownDataSource(Exception):
    ...