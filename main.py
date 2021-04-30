import argparse
import os
import re
import platform
import sys
import subprocess
import logging


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, ROOT_DIR)


with open("core_checker.log", "w") as f:    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("core_checker.log"),
        logging.StreamHandler()
    ]
)


username = os.environ.get('USERNAME')
python_version = sys.version
os_type = sys.platform
os_version = platform.platform()


def get_processer_info():
    """
    Get processor information in windows using WMIC.

    Output example:
    Manufacturer  Name                                      NumberOfCores  ThreadCount
    GenuineIntel  Intel(R) Core(TM) i5-6300U CPU @ 2.40GHz  2              4

    Retval:
    List in format of
    [Manufacturer, Name, NumberOfCores, ThreadCount]
    """
    info_list = []
    output = subprocess.check_output("wmic cpu get Manufacturer,Name,ThreadCount, NumberOfCores").decode()
    output = output.replace("\r\r", "").split("\n")[1] # Remove the \r\r then extract the second line only
    output = re.split(r"\s{2,14}?", output)

    for element in output:
        if element != "" and element != " ":
            info_list.append(element)
        
    return info_list

print(get_processer_info())
parser = argparse.ArgumentParser()
parser.add_argument("-ct", "--core_type", help="physical(p) or logical(l), DEFAULT=logical",type=str, nargs=1, default="logical")
#parser.add_argument('-expnumc', '--expected_number_of_core', 
#                    help=f"Expected number of cores. DEFAULT=Number of logical cores ({logical_core})", 
#                    type=int,
#                    default=logical_core)


args = parser.parse_args()
print(args)

#logging.info("====================================")
#logging.info("         SYSTEM INFORMATION         ")
#logging.info("====================================")
#logging.info(f"CPU NAME: {cpu_name}")
#logging.info(f"CPU ARCH: {cpu_arch}")
#logging.info(f"USER: {username}")
#logging.info(f"Python version: {python_version}")
#logging.info(f"OS type: {os_type}")
#logging.info(f"OS version: {os_version}")
#logging.info(f"Number of Physical Cores: {physical_core}")
#logging.info(f"Number of Logical Cores: {logical_core}")


