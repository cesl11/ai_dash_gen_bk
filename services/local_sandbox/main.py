"Creates a local sandbox service, using Jupyter Notebook kernel."

"""It only allows text-to-text communication via local API,"
based on the work of Anton Shemyakov: https://dida.do/blog/setting-up-a-secure-python-sandbox-for-llm-agents."""

"""This is an on-premise solution, enough for local and simple data exploration, analysis and
code generation. However, for high-level production enviroments, with large-scale data and more robust
security needs, I highly recommend use the `E2B` standard solution."""

import os
import sys
# Add project root to sys.path for aux imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import asyncio
from asyncio import TimeoutError, wait_for
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from jupyter_client.manager import AsyncKernelManager

from aux.validators.models.request_models import (
    CodeRequest,
    InstallRequest,
    ExecutionResult
)
from exceptions.code_execution.code_execution_exc import LocalSandboxExecutionError


# -- App setting up
app = FastAPI()

allowed_packages = ['numpy', 'scipy', 'pandas', 'matplotlib', 'scikit-learn', 'openpyxl']
installed_packages: List[str] = []


# -- Functs
@asynccontextmanager
async def kernel_client_python():
    """Manages Jupyter kernel."""
    km = AsyncKernelManager(kernel_name='python3')
    await km.start_kernel()
    kc = km.client()
    kc.start_channels()
    await kc.wait_for_ready()
    try:
        yield kc
    finally:
        kc.stop_channels()
        await km.shutdown_kernel()

        
async def execute_code(code: str) -> str:
    """Using an existing kernel, executes code inside it."""
    async with kernel_client_python() as kc:
        msg_id = kc.execute(code)
        try:
            for i in range(5):
                reply = await kc.get_iopub_msg()
                if reply['parent_header']['msg_id'] != msg_id:
                    continue
                msg_type = reply['msg_type']
                if msg_type == 'stream':
                    return reply['content']['text']
                elif msg_type == 'error':
                    raise LocalSandboxExecutionError(f"Error executing code: {reply['content']['evalue']}")
                elif msg_type == 'status' and reply['content']['execution_state'] == 'idle':
                    break
        except asyncio.CancelledError:
            raise
    return ""

async def install_package(package: str) -> None:
    """Install a package in the existing kernel."""
    if package not in installed_packages and package in allowed_packages:
        async with kernel_client_python() as kc:
            try:
                kc.execute(f"!pip install {package}")
                while True:
                    reply = await kc.get_iopub_msg()
                    if (
                        reply['msg_type'] == 'status'
                        and reply['content']['execution_state'] == 'idle'
                    ):
                        break
                installed_packages.append(package)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error installing package: {str(e)}")



# -- Endpoints
@app.post('/install')
async def install(request: InstallRequest):
    try:
        await wait_for(install_package(request.package), timeout=120)
    except TimeoutError:
        raise HTTPException(status_code=400, detail='Package installation timed out.')
    return {'message': f"Requested package {request.package} installed succcesfully."}


@app.post('/execute', response_model=ExecutionResult)
async def execute(request: CodeRequest) -> ExecutionResult:
    try:
        output =  await wait_for(execute_code(request.code), timeout=120)
    except TimeoutError:
        raise HTTPException(status_code=400, detail='Code execution timed out.')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical code execution error: {str(e)}")           
    
    
    
# -- Running as requested
if __name__ == '__name__':
    import uvicorn
    
    uvicorn.run(app, host='127.0.0.1', port=8000)