"""
eXuCoDeR Music Bot - Plugin Loader
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import os
import importlib
import logging

logger = logging.getLogger(__name__)

all_modules = []

# Auto-discover all plugin modules
for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and not filename.startswith("_"):
        module_name = filename[:-3]
        all_modules.append(module_name)
        try:
            importlib.import_module(f"anony.plugins.{module_name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {module_name}: {e}")

all_modules = sorted(set(all_modules))
logger.info(f"Discovered {len(all_modules)} plugins: {', '.join(all_modules)}")
