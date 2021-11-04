import argparse
import os
import re
import platform
import sys
import subprocess
import logging


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, ROOT_DIR)

"""
For Ubuntu, 
somehow the log files generated will have lock icon.
Observed this after adding alias to ~/.bashrc

To solve this,
sudo chown -R $USER: $HOME
from https://askubuntu.com/a/263454
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(filename="core_checker.log", mode="w"),
        logging.StreamHandler()
    ]
)


hostname = platform.node()
username = os.environ.get('USERNAME')
python_version = sys.version
os_type = platform.system()
os_version = platform.platform()

cpu_info_list = [
    # cpu_vendor_id
    # cpu_model_name 
    # physical_core_count
    # logical_core_count 
]
CPU_VENDOR_ID = 0
CPU_MODEL_NAME = 1
CPU_PHYSICAL_CORES = 2
CPU_LOGICAL_CORES = 3

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
    with open("wmic_cpu_stdout.log", "w") as f: f.write(output.replace("\r\r", ""))
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
    with open("lscpu_stdout.log", "w") as f: f.write(output)
    for regex in LSCPU_REGEX_DICT.values():
        info_list.append(re.findall(regex, output)[0])
    return info_list


def get_cpu_info():
    """
    Return a list with basic cpu information such as

    Vendor ID, CPU Name, Number of Physical & Logical Cores
    """
    if os_type == "Windows":
        return get_cpu_info_windows()
    else:
        return get_cpu_info_linux()

def set_cpu_info_list():
    """
    Set the cpu_info_list after calling get_cpu_info()
    """
    _cpu_info_list = get_cpu_info()

    if os_type == "Windows":
        for value in WMIC_CPUINFO_LIST_INDEX.values():
            cpu_info_list.append(_cpu_info_list[value])
    else:
        for value in LSCPU_CPUINFO_LIST_INDEX.values():
            cpu_info_list.append(_cpu_info_list[value])

def show_system_info():
    """"
    Log the system info to stdout and a file.
    """
    logging.info("====================================")
    logging.info("         SYSTEM INFORMATION         ")
    logging.info("====================================")
    logging.info(f"CPU VENDOR: {cpu_info_list[0]}")
    logging.info(f"CPU NAME: {cpu_info_list[1]}")
    logging.info(f"Number of Physical Cores: {cpu_info_list[2]}")
    logging.info(f"Number of Logical Cores: {cpu_info_list[3]}")
    logging.info("")
    logging.info(f"USER: {username}")
    logging.info(f"HOSTNAME: {hostname}")
    logging.info(f"Python version: {python_version}")
    logging.info(f"OS type: {os_type}")
    logging.info(f"OS version: {os_version}")
    logging.info("====================================")

def arg_init():
    """
    Initialize argparse with default variables.

    Retval:
    Namespace of initialized arguments
    
    NOTE:
    Expect these functions to be called before invoke this function
    1.  get_cpu_info()
    2.  set_cpu_info_list()
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-epc', '--expected_physical_cores', 
                       help=f"Expected number of physical cores.", 
                       type=int)
    parser.add_argument('-elc', '--expected_logical_cores', 
                    help=f"Expected number of logical cores.", 
                    type=int)                   
    args = parser.parse_args()
    return args


def argument_not_specified(args_dict):
    """
    Return True if all the values in args_dict is None,
    else return False

    Args:
    args_dict: argparse namespace object in dict    
    """
    if all(value is None for value in args_dict.values()):
        return True
    return False


def core_checker(core_type, expected_value):
    """
    Check the number of physical/logical cores.
    Must call these functions first
    1.  get_cpu_info()
    2.  set_cpu_info_list()

    Args:
        core_type (str): Either is or contain "logical", "physical", case insensitive
        expected_value (int): Expected number of cores for core_type
    """
    core_type = core_type.lower()

    if "logical" in core_type:
        if int(cpu_info_list[CPU_LOGICAL_CORES]) != expected_value:
            logging.error(f"Expected Logical Cores: {expected_value}, Actual: {cpu_info_list[CPU_LOGICAL_CORES]}")
            logging.error(f"Exiting with exit code 1")
            exit(1)
        logging.info(f"Actual Logical Cores is same as expected ({expected_value})")
        return True
    elif "physical" in core_type:
        if int(cpu_info_list[CPU_PHYSICAL_CORES]) != expected_value:
            logging.error(f"Expected Physical Cores: {expected_value}, Actual: {cpu_info_list[CPU_PHYSICAL_CORES]}")
            logging.error(f"Exiting with exit code 1")
            exit(1)
        logging.info(f"Actual Physical Cores is same as expected ({expected_value})")    
        return True
    else:
        raise ValueError(f"Invalid option received (core_type) for 'core_type'")



def process_arg(args):
    """
    Process the arguments(args) after calling arg_init()
    """
    args_dict = args.__dict__

    if argument_not_specified(args_dict):
        logging.warning("No arguments specified, assuming no checking is needed.")
        logging.warning("Exit with exit code 0")
        exit(0)
    else:
        for key, value in args_dict.items():
            if value is not None:
                core_checker(key, value)
        # core_checker will exit(1) if either/both of the physical and logical cores
        # does not matched the expected value specified in argument.
        # If it can make it through here, then the number of physical/logical cores 
        # are same as expected.
        logging.warning("Exit with exit code 0")
        exit(0)

        
if __name__ == "__main__":
    get_cpu_info()
    set_cpu_info_list()
    show_system_info()

    args = arg_init()
    process_arg(args)



