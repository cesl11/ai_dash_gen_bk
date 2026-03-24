"Defines tools to powered-by-LLM chart creation."

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from langchain_core.tools import tool
from models.charts.chart_models import ChartFactory

# --- Here starts
@tool()
def createChart(chartType: str): 
    # AQUÍ lo que queda pendiente es pensar COMO el modelo pasará los argumentos, que van a variar según el tipo de dato.
    # :P Se necesita implementar alguna lógica de validación
    chartInstance = ChartFactory.createChartInstance(chartType)
    chartConfig = chartInstance.getConfig()
    return chartConfig