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

cpu_info_list = [
    # cpu_vendor_id
    # cpu_model_name 
    # physical_core_count
    # logical_core_count 
]

LSCPU_REGEX_DICT = {
    "LSCPU_CPU_REGEX": "\nCPU\(s\): \s*(\d*)",
    "LSCPU_SOCKET_REGEX": "Socket\(s\):\s*(\d*)",
    "LSCPU_VENDOR_ID_REGEX": "Vendor ID:\s*(\w*)",
    "LSCPU_MODEL_NAME_REGEX": "Model name:\s*(.*)",
    "LSCPU_THREADS_PER_CORE_REGEX": "Thread\(s\) per core:\s*(\d*)",
    "LSCPU_CORES_PER_SOCKET_REGEX": "Core\(s\) per socket:\s*(\d*)"
}

LSCPU_CPUINFO_LIST_INDEX = {
    "LSCPU_VENDOR_ID_INDEX": 2,
    "LSCPU_MODEL_NAME_INDEX": 3,
    "LSCPU_CORES_PER_SOCKET_INDEX": 5,  # Physical cores
    "LSCPU_NUMBER_OF_CPU_INDEX": 0,     # Logical cores
    "LSCPU_NUMBER_OF_SOCKET_INDEX": 1,
    "LSCPU_THREADS_PER_SOCKET_INDEX": 4
}

WMIC_CPUINFO_LIST_INDEX = {
    "WMIC_VENDOR_ID_INDEX": 0,
    "WMIC_MODEL_NAME_INDEX": 1,
    "WMIC_NUMBER_OF_CORES": 2,    # Physical cores
    "WMIC_NUMBEROF_THREADS": 3    # Logical cores
}

def get_cpu_info():
    """
    Return a list with basic cpu information such as

    Vendor ID, CPU Name, Number of Physical & Logical Cores
    """
    if os_type is "Windows":
        return get_cpu_info_win()
    else:
        return get_cpu_info_linux()


def get_cpu_info_windows():
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


def get_cpu_info_linux():
    """
    Get processor information in linux using lscpu command and re.

    From putput of lscpu
    Number of Threads/Logical Procesor = Cpu(s)
    Number of Physical Cores = CoresPerSocket * Socket(s)

    Retval:
    List in format of 
    [Cpu(s), Socket(s), VendorID, ModelName,ThreadsPerCore, CoresPerSocket]
    """
    info_list = []
    output = subprocess.check_output("lscpu").decode()
    for regex in LSCPU_REGEX_DICT.values():
        info_list.append(re.findall(regex, output)[0])
    return info_list


def set_cpu_variable():
    _cpu_info_list = get_cpu_info()

    if os_type is "Windows":
        for value in WMIC_CPUINFO_LIST_INDEX.values():
            cpu_info_list.append(_cpu_info_list[value])
    else:
        for value in LSCPU_CPUINFO_LIST_INDEX.values():
            cpu_info_list.append(_cpu_info_list[value])


parser = argparse.ArgumentParser()
parser.add_argument("-ct", "--core_type", help="physical(p) or logical(l), DEFAULT=logical",type=str, nargs=1, default="logical")
#parser.add_argument('-expnumc', '--expected_number_of_core', 
#                    help=f"Expected number of cores. DEFAULT=Number of logical cores ({logical_core})", 
#                    type=int,
#                    default=logical_core)

get_cpu_info()
set_cpu_variable()
args = parser.parse_args()

logging.info("====================================")
logging.info("         SYSTEM INFORMATION         ")
logging.info("====================================")
logging.info(f"CPU VENDOR: {cpu_info_list[0]}")
logging.info(f"CPU NAME: {cpu_info_list[1]}")
logging.info(f"Number of Physical Cores: {cpu_info_list[2]}")
logging.info(f"Number of Logical Cores: {cpu_info_list[3]}")
logging.info("")
logging.info(f"USER: {username}")
logging.info(f"Python version: {python_version}")
logging.info(f"OS type: {os_type}")
logging.info(f"OS version: {os_version}")


