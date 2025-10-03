"""Shared runtime state for the Personal Finance app.

This module holds small global state objects that are safe to import from
multiple modules without creating circular import problems.
"""
from typing import List, Dict

transactions: List[Dict] = []
