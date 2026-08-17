from .base import *

CURRENT_ENV = "production"

# Hardcoded regardless of base/env config as a safety net — production must never run with DEBUG on.
DEBUG = False
