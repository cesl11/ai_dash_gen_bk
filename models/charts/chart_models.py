"Define the chart interfaces notions."

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from abc import ABC, abstractmethod
from aux.default_colors import defaultBgColors, defaultBorderColors
from aux.decorators import validate
from typing import Dict, List

# Abstract interfaces
class Chart(ABC):
    """Common interface for any chart."""
    @abstractmethod
    def getConfig(self) -> Dict:
        """Send to the agent the chart config for the chart."""
        ...
        
class BarChart(Chart):
    @validate
    def getConfig(self, labels: List[str], dataArray: List[float], 
        backgroundColors: List[str] = defaultBgColors, borderColors: List[str] = defaultBorderColors, 
        borderWidth: int = 1, beginAtZeroInY: bool = True):
        try:
            data = {
                'labels': labels,
                'data': dataArray,
                'backgroundColor': backgroundColors,
                'borderColor': borderColors,
                'borderWidth': borderWidth
            }
            return {
                'type': 'bar',
                'data': data,
                'options': {
                    'scales': {
                        'y': {'beginAtZero': beginAtZeroInY}
                    }
                }
            }
        except Exception as e:
            raise Exception(f'Critical error while getting BAR CHART config: {e}')

x = BarChart().getConfig(labels='hola', dataArray=[23.4, 2.5])
print(x)