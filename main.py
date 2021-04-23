import os
import platform
import sys
import logging

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, ROOT_DIR)

# Linux system comes with psutil (on Ubuntu 20.04.1 LTS)
if platform.system() == "Windows":	from lib import psutil
else:	import psutil

with open("core_checker.log", "w") as f:    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("core_checker.log"),
        logging.StreamHandler()
    ]
)

physical_core = psutil.cpu_count(logical = False)
logical_core = psutil.cpu_count(logical = True)

logging.info(f"Number of Physical Cores: {physical_core}")
logging.info(f"Number of Logical Cores: {logical_core}")
