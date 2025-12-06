"""
BVM API Compare PSP Entry Tool

This script provides functionality to compare PSP entries between different BIOS versions
using the BVM API.
"""

import os
import requests
import json
import sys
import logging
from typing import Optional, Tuple, Dict, Any, List

# ==================== CONSTANTS ==================== #
BASE_URL = "http://bvm/"
# BASE_URL = "https://localhost:44379/"
VERSION = "1.00"

# Logging configuration
logger = logging.getLogger(__name__)
FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.INFO)

# ==================== CONFIGURATION ==================== #
# Modify these values as needed
USERNAME = "boyachen"
PASSWORD = "***"
PURPOSE = "BVMAPI test"
CMP_PROGRAM = "BRH"

# Below are Base BIOS selection

# Weekly BIOS Configuration
PROCESSOR_NAME = "ShimadaPeak - Family 1Ah"
PLATFORM_NAME = "Rev_SHP_BoulderGulch_AMD_EDKII"
BASE_BIOS_TYPE = "Weekly BIOS"  # Available: Weekly BIOS, PI BIOS, User-Generated, By Request Id
REVISION = "WBK5709N_196"

# PI BIOS Configuration (commented out)
"""
PROCESSOR_NAME = "ShimadaPeak - Family 1Ah"
PLATFORM_NAME = "Rev_SHP_BoulderGulch_AMD_EDKII"
BASE_BIOS_TYPE = "PI BIOS"
REVISION = "TBK1001C_175"
"""

# By Request Id Configuration (commented out)
"""
PROCESSOR_NAME = "ShimadaPeak - Family 1Ah"
PLATFORM_NAME = "Rev_SHP_BoulderGulch_AMD_EDKII"
BASE_BIOS_TYPE = "By Request Id"
REVISION = "1245857"
"""

# User-Generated Configuration (commented out)
"""
PROCESSOR_NAME = "ShimadaPeak - Family 1Ah"
PLATFORM_NAME = "Rev_SHP_BoulderGulch_AMD_EDKII"
BASE_BIOS_TYPE = "User-Generated"
REVISION = r"D:\Input\BVM\WBK4B06N_102.FD"
"""

# Below are Compare BIOS selection

# User-Generated Configuration
CMP_BIOS_TYPE = "User-Generated"
CMP_REVISION = r"D:\Input\BVM\WBK4B06N_102.FD"

# PI BIOS Configuration (commented out)
"""
CMP_BIOS_TYPE = "PI BIOS"
CMP_REVISION = "TBK1001C_175"
"""

# By Request Id Configuration (commented out)
"""
CMP_BIOS_TYPE = "By Request Id"
CMP_REVISION = "1245857"
"""

# Weekly BIOS Configuration (commented out)
"""
CMP_BIOS_TYPE = "Weekly BIOS"
CMP_REVISION = "WBK5709N_196"
"""

NEW_NAME = ""  # Leave blank for default name

# ==================== API FUNCTIONS ==================== #

def login(username: str, password: str) -> Optional[str]:
    """Authenticate user and return access token."""
    logger.info("Logging in...")
    url = f"{BASE_URL}api/account/Login"
    credentials = {
        "userName": username,
        "Password": password
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(credentials), verify=False)
        if response.status_code == 200:
            logger.info("Login successful")
            return response.json()['token']
        elif response.status_code == 401:
            logger.error("Login failed. Please check your username and password.")
        else:
            logger.error(f"Login failed. Status code: {response.status_code}. Reason: {response.reason}")
    except requests.RequestException as e:
        logger.error(f"Login request failed: {e}")
    
    return None


def get_processor_list(token: str) -> Optional[List[Dict[str, Any]]]:
    """Retrieve list of available processors."""
    logger.info("Getting processor list...")
    url = f"{BASE_URL}api/bvmmain/GetProcessorList"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            logger.info("Get processor list successful")
            return json.loads(response.text)
        elif response.status_code == 401:
            logger.error("Get processor list failed. Please check your credentials.")
        else:
            logger.error(f"Get processor list failed. Status code: {response.status_code}. Reason: {response.reason}")
    except requests.RequestException as e:
        logger.error(f"Get processor list request failed: {e}")
    
    return None


def get_processor_id(processor_list: List[Dict[str, Any]], processor_name: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Find processor ID by name."""
    for processor in processor_list:
        if processor["name"] == processor_name:
            return processor["id"], processor
    return None, None


def get_platform_id(processor: Dict[str, Any], platform_name: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Find platform ID by name within a processor."""
    for platform in processor["platforms"]:
        if platform["name"] == platform_name:
            return platform["id"], platform
    return None, None


def get_weekly_bios_id(platform: Dict[str, Any], revision: str) -> Optional[str]:
    """Get Weekly BIOS ID by revision name."""
    for weekly_bios in platform["weeklyBIOSes"]:
        if weekly_bios["name"] == revision:
            return weekly_bios["id"]
    return None


def get_pi_bios_id(platform: Dict[str, Any], revision: str) -> Optional[str]:
    """Get PI BIOS ID by revision name."""
    for pi_bios in platform["piBIOSes"]:
        if pi_bios["name"] == revision:
            return pi_bios["id"]
    return None


def upload_user_gen_bios(revision: str, token: str) -> Optional[str]:
    """Upload user-generated BIOS file."""
    url = f"{BASE_URL}api/bvmmain/UploadBaseBIOS?name=filename"
    bios_filename = os.path.basename(revision)
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (bios_filename, open(revision, 'rb'))}

    try:
        response = requests.post(url, files=files, headers=headers, verify=False)
        if response.status_code == 200:
            return response.content.decode("ascii")
        else:
            logger.error(f"Upload user-gen BIOS failed. Status code: {response.status_code}. Reason: {response.reason}")
    except requests.RequestException as e:
        logger.error(f"Upload user-gen BIOS request failed: {e}")
    except FileNotFoundError:
        logger.error(f"BIOS file not found: {revision}")
    
    return None


def get_revision(platform: Dict[str, Any], bios_type: str, revision: str, token: str) -> Optional[str]:
    """Get revision ID based on BIOS type."""
    if bios_type == "Weekly BIOS":
        return get_weekly_bios_id(platform, revision)
    elif bios_type == "PI BIOS":
        return get_pi_bios_id(platform, revision)
    elif bios_type == "User-Generated":
        return upload_user_gen_bios(revision, token)
    elif bios_type == "By Request Id":
        return revision
    return None


def generate_compare_psp_entry_request(
    processor_list: List[Dict[str, Any]], 
    processor_name: str, 
    platform_name: str, 
    base_bios_type: str, 
    revision: str, 
    cmp_revision: str, 
    purpose: str, 
    new_name: str,
    token: str
) -> Optional[str]:
    """Generate Compare PSP Entry Request."""
    logger.info("Generating Compare PSP Entry Request...")
    
    # Get processor ID
    processor_id, processor = get_processor_id(processor_list, processor_name)
    if processor_id is None:
        logger.error("Failed to get processor ID")
        return None

    # Get platform ID
    platform_id, platform = get_platform_id(processor, platform_name)
    if platform_id is None:
        logger.error("Failed to get platform ID")
        return None

    # Get base revision
    base_revision = get_revision(platform, base_bios_type, revision, token)
    if base_revision is None:
        logger.error("Failed to get base revision")
        return None

    # Get comparison revision
    comparison_revision = get_revision(platform, CMP_BIOS_TYPE, cmp_revision, token)
    if comparison_revision is None:
        logger.error("Failed to get comparison revision")
        return None

    # Generate request
    url = f"{BASE_URL}api/bvmcompare/GenerateCompareRequest"
    headers = {"Authorization": f"Bearer {token}"}
    parameters = {
        "processorId": processor_id,
        "platformId": platform_id,
        "baseBIOSType": base_bios_type,
        "revision": base_revision,
        "cmpBIOSType": CMP_BIOS_TYPE,
        "cmp_revision": comparison_revision,
        "cmp_program": CMP_PROGRAM,
        "purpose": purpose,
        "newName": new_name,
        "isApi": "1"
    }

    try:
        response = requests.get(url, params=parameters, headers=headers, verify=False)
        if response.status_code == 200:
            logger.info("Generate Compare PSP Entry Request successful")
            return response.text
        else:
            logger.error(f"Generate Compare PSP Entry Request failed. Status code: {response.status_code}. Reason: {response.reason}")
    except requests.RequestException as e:
        logger.error(f"Generate Compare PSP Entry Request failed: {e}")
    
    return None


def update_name(request_id: str, update_name: str, token: str) -> Optional[int]:
    """Update request name."""
    logger.info("Updating name...")
    url = f"{BASE_URL}api/bvmmain/UpdateNewName?requestId={request_id}&newName={update_name}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            logger.info("Update name successful")
            return 1
        else:
            logger.error(f"Update name failed. Status code: {response.status_code}. Reason: {response.reason}")
    except requests.RequestException as e:
        logger.error(f"Update name request failed: {e}")
    
    return None


def get_psp_entry_diff(request_id: str, token: str) -> None:
    """Get PSP Entry Diff and display results."""
    logger.info("Getting PSP Entry Diff...")
    url = f"{BASE_URL}api/bvmcompare/GetPspDiff?requestId={request_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            logger.info("Get PSP Entry Diff successful")
            logger.info(f"The compare result page is: http://bvm/bvm/compare/{request_id}")
            logger.info("Compare BIOS PSP entry task is finished successfully")
        else:
            logger.error(f"Get PSP Entry Diff failed. Status code: {response.status_code}. Reason: {response.reason}")
            logger.info("Compare BIOS PSP entry task failed")
    except requests.RequestException as e:
        logger.error(f"Get PSP Entry Diff request failed: {e}")
        logger.info("Compare BIOS PSP entry task failed")


# ==================== MAIN FUNCTION ==================== #


def main() -> None:
    """Main execution function."""
    # Login
    token = login(USERNAME, PASSWORD)
    if not token:
        return

    # Get processor list
    processor_list = get_processor_list(token)
    if not processor_list:
        return

    # Generate compare request
    request_id = generate_compare_psp_entry_request(
        processor_list, 
        PROCESSOR_NAME, 
        PLATFORM_NAME, 
        BASE_BIOS_TYPE, 
        REVISION, 
        CMP_REVISION, 
        PURPOSE, 
        NEW_NAME, 
        token
    )
    if not request_id:
        return
    
    # Remove quotes from request ID
    request_id = request_id.replace('"', "")

    # Get PSP entry diff
    get_psp_entry_diff(request_id, token)


if __name__ == "__main__":
    main()