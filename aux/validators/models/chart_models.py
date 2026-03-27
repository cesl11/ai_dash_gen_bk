"Define the chart base models for LLM output validation."

import os
import sys
# Add project root to sys.path for aux imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pydantic import BaseModel, field_validator
from aux.default_settings.default_colors import defaultBgColors, defaultBorderColors
from typing import List, Any


# -- Common classes used by all charts -- #

# -- Colors
class RGBColor(BaseModel):
    """Color string parser"""
    r: int
    g: int
    b: int
    a: float = 1.0 

    @field_validator("r", "g", "b")
    @classmethod
    def validate_rgb(cls, v):
        if not (0 <= v <= 255):
            raise ValueError('RGB values must be between 0 and 255')
        return v

    @field_validator("a")
    @classmethod
    def validate_alpha(cls, v):
        if not (0 <= v <= 1):
            raise ValueError('Alpha must be between 0 and 1')
        return v


# -- Scales
class YScale(BaseModel):
    beginAtZero: bool = True

class Scales(BaseModel):
    y: YScale
    

# --- Charts --- #

# -- Bar 
class BarChartDatasets(BaseModel):
    label: str
    data: List[Any]
    backgroundColor: List[RGBColor] = defaultBgColors
    borderColor: List[RGBColor] = defaultBorderColors
    borderWidth: int = 1
    
class BarChartData(BaseModel):
    labels: List[str]
    datasets: List[BarChartDatasets]

class BarChartOptions(BaseModel):
    scales: Scales
    
class BarChart(BaseModel):
    """Main bar chart validator"""
    type: str = 'bar'
    data: BarChartData
    options: BarChartOptions
