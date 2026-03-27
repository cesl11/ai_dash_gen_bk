"Defines structures for local sandbox requests."
from pydantic import BaseModel

# -- Here starts
class CodeRequest(BaseModel):
    code: str
    
class InstallRequest(BaseModel):
    package: str
    
class ExecutionResult(BaseModel):
    output: str
