"""
Data Analyst Module
Location: api/backend/studylink/data_analyst/__init__.py

This module contains all routes for Persona 1: Jordan Lee (Data Analyst)
"""

from backend.studylink.data_analyst.analyst_routes import analyst
from backend.studylink.data_analyst.dataset_routes import datasets
from backend.studylink.data_analyst.metric_routes import metrics

__all__ = ['analyst', 'datasets', 'metrics']