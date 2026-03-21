"Defines tools to powered-by-LLM chart creation."

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from langchain_core.tools import tool
from typing import Dict, Any

# --- Here starts
@tool
def createChart(chartConfig: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(chartConfig, dict):
        raise TypeError("'chartConfig' arg must be a dictionary.")
    requiredConfigInfo = ['type', 'data', 'datasets']
    for configInfo in requiredConfigInfo:
        assert configInfo in chartConfig
    # Default settings
    if not chartConfig['options']:
        chartConfig.setdefault('options', {})
        chartConfig['options'].setdefault('responsive', True)
        chartConfig['options'].setdefault('plugins', {})
    
        plugins = chartConfig['options']['plugins']
        plugins.setdefault('title', {
            'display': False,
            'text': ""
        })
    for dataset in chartConfig['data']['datasets']:
        if 'data' not in dataset:
            raise ValueError("Each dataset must have 'data'")
        dataset.setdefault('backgroundColor', 'rgba(75, 192, 192, 0.5)')
        dataset.setdefault('borderColor', 'rgba(75, 192, 192, 1)')
        dataset.setdefault('borderWidth', 1)
    return chartConfig