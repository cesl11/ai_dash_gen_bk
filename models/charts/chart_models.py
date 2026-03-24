"Define the chart interfaces notions."

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from abc import ABC, abstractmethod
from aux.default_colors import defaultBgColors, defaultBorderColors
from aux.decorators import validate
from exceptions.arg_validation_exceptions import UnmatchingLabelAndDataArraySize
from exceptions.chart_exceptions import UnknownChartType
from datetime import datetime
from typing import List

# Abstract interfaces
class Chart(ABC):
    """Common interface for any chart."""
    @abstractmethod
    def getConfig(self) -> dict:
        """Send to the agent the chart config for the chart."""
        ...
        
class BarChart(Chart):
    @validate
    def getConfig(self, 
                    chartTitle: str,
                    labels: List[str], 
                    dataArray: List[float | int | datetime],
                    backgroundColors: List[str] = defaultBgColors, 
                    borderColors: List[str] = defaultBorderColors, 
                    borderWidth: int = 1, beginAtZeroInY: bool = True) -> dict:
        labelsLenght = len(labels)
        dataArrayLenght = len(dataArray)
        if labelsLenght != dataArrayLenght:
            raise UnmatchingLabelAndDataArraySize(f"Size of 'labels' object ({labelsLenght} elements) does not match with size of 'dataArray' object ({dataArrayLenght} elements).")
        try:
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': chartTitle,
                            'data': dataArray,
                            'backgroundColor': backgroundColors,
                            'borderColor': borderColors,
                            'borderWidth': borderWidth
                        }
                    ]
                },
                'options': {
                    'scales': {
                        'y': {
                            'beginAtZero': beginAtZeroInY
                        }
                    }
                }
            }
        except UnmatchingLabelAndDataArraySize:
            raise
        except Exception as e:
            raise Exception(f'Critical error while getting BAR CHART config: {e}')


# Main factory class
class ChartFactory:
    _registry: dict[str, type[Chart]] = {
        #       Bar charts
        'simple_bar_chart':BarChart
    }
    
    @classmethod
    def registerNewChart(cls, name: str, kclass: type[Chart]) -> None:
        """Registers a new data source."""
        cls._registry[name] = kclass
        
    @classmethod
    def createChartInstance(cls, chartType: str) -> Chart:
        """Creates a new source instance for working with."""
        kclass = cls._registry.get(chartType)
        if not kclass:
            availableCharts = list(cls._registry.keys())
            raise UnknownChartType(f"Chart type not available: '{chartType}'."
                             f"Supported charts: '{availableCharts}'")
        return kclass()