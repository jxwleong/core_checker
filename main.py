import argparse
import os
import platform
import sys
import logging

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, ROOT_DIR)

# Linux system comes with psutil (on Ubuntu 20.04.1 LTS)
if platform.system() == "Windows":	 from lib import psutil
#if platform.system() == "Windows":	 import lib.psutil as psutil
else:	import psutil

#import lib.cpuinfo

with open("core_checker.log", "w") as f:    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("core_checker.log"),
        logging.StreamHandler()
    ]
)

#CPU_INFO_DICT = cpuinfo.get_cpu_info()

#cpu_name = CPU_INFO_DICT["brand_raw"]
#cpu_arch = CPU_INFO_DICT["arch"]
username = os.environ.get('USERNAME')
python_version = sys.version
os_type = sys.platform
os_version = platform.platform()
physical_core = psutil.cpu_count(logical = False)
logical_core = psutil.cpu_count(logical = True)


parser = argparse.ArgumentParser()
parser.add_argument("-ct", "--core_type", help="physical(p) or logical(l), DEFAULT=logical",type=str, nargs=1, default="logical")
parser.add_argument('-expnumc', '--expected_number_of_core', 
                    help=f"Expected number of cores. DEFAULT=Number of logical cores ({logical_core})", 
                    type=int, 
                    default=logical_core)


args = parser.parse_args()
print(args)

logging.info("====================================")
logging.info("         SYSTEM INFORMATION         ")
logging.info("====================================")
#logging.info(f"CPU NAME: {cpu_name}")
#logging.info(f"CPU ARCH: {cpu_arch}")
logging.info(f"USER: {username}")
logging.info(f"Python version: {python_version}")
logging.info(f"OS type: {os_type}")
logging.info(f"OS version: {os_version}")
logging.info(f"Number of Physical Cores: {physical_core}")
logging.info(f"Number of Logical Cores: {logical_core}")


