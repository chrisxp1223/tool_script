"""
PSP Replacement v2.0 - 使用Configuration系統

Improvements:
- 使用 BvmClient Basic類別
- 支援Configuration檔案
- Object-oriented design
- Better error handling
"""

import requests
import json
from enum import Enum
from typing import List, Dict, Any, Optional
from bvm_client import BvmClient
from bvm_config import BvmConfig


class EntryOperationType(Enum):
    """PSP entry operation type"""
    Add = 0
    Remove = 1
    Modify = 2


class PspReplacer(BvmClient):
    """PSP entry replacement client"""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None,
                 config: Optional[BvmConfig] = None, config_file: Optional[str] = None):
        """
        Initialize PSP Replacer

        Args:
            username: BVM username (Optional，If using config)
            password: BVM password (Optional，If using config)
            config: BvmConfig instance (Optional)
            config_file: Configuration file path (Optional)
        """
        # Call parent class initialization (will auto login)
        super().__init__(username=username, password=password,
                        config=config, config_file=config_file)

    def get_available_operations(self) -> Dict[str, str]:
        """
        Get可用的Operation type

        Returns:
            Operation type dictionary
        """
        url = f"{self.base_url}api/bvmpsp/GetAvailableOperations"
        response = requests.get(url)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception(f"Get available operations failed. Status code: {response.status_code}. Reason: {response.reason}")

    def _get_operation_type_str(self, operation_type: str) -> str:
        """
        GetOperation type字串

        Args:
            operation_type: Operation type (For example: "PSP")

        Returns:
            Operation type字串
        """
        available_ops = self.get_available_operations()

        for key, value in available_ops.items():
            if value == operation_type:
                return key

        raise Exception(f"Operation type not found: {operation_type}")

    def generate_psp_request(self, processor_name: str, platform_name: str,
                            bios_type: str, revision: str, operation_type: str,
                            purpose: str, psp_config: str, new_name: str = "") -> str:
        """
        Generate PSP request

        Args:
            processor_name: Processor name
            platform_name: Platform name
            bios_type: BIOS type
            revision: 版本
            operation_type: Operation type
            purpose: Purpose
            psp_config: PSP Configuration
            new_name: New name (Optional)

        Returns:
            Request ID
        """
        # Get processor 和 platform ID
        proc_id, proc = self.get_processor_id(processor_name)
        plat_id, plat = self.get_platform_id(proc, platform_name)

        # Get revision ID
        rev_id = self.get_revision(plat, bios_type, revision)

        # GetOperation type字串
        op_type_str = self._get_operation_type_str(operation_type)

        # Generate request
        url = f"{self.base_url}api/bvmpsp/GeneratePspRequest"
        headers = self._get_auth_headers()

        params = {
            "processorId": proc_id,
            "platformId": plat_id,
            "baseBIOSType": bios_type,
            "revision": rev_id,
            "operationType": op_type_str,
            "purpose": purpose,
            "newName": new_name,
            "isApi": 1,
            "selectedPspConfig": psp_config
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            request_id = response.text.replace('"', '')
            self.logger.info(f"Generate PSP Request successful. Request ID: {request_id}")
            return request_id
        else:
            raise Exception(f"Generate PSP Request failed. Status code: {response.status_code}. Reason: {response.reason}")

    def upload_psp_entries(self, request_id: str, replacement_list: List[Dict[str, Any]]) -> None:
        """
        Upload PSP entries

        Args:
            request_id: Request ID
            replacement_list: Replacement list
        """
        self.logger.info("Uploading PSP entries...")
        url = f"{self.base_url}api/bvmpsp/UploadPspEntry"
        headers = self._get_auth_headers()

        for entry in replacement_list:
            # Skip Remove operation and type 0x7
            if entry.get("operation") == EntryOperationType.Remove.value:
                continue
            if entry.get("type") == "0x7":
                continue

            # Build upload URL
            upload_url = url
            upload_url += f"?dirType={'PSP' if entry['isPspEntry'] else 'BIOS'}"
            upload_url += f"&type={entry['type']}"
            upload_url += f"&romId={entry['romId']}"
            upload_url += f"&instance={entry['instance']}"
            upload_url += f"&subProgram={entry['subProgram']}"
            upload_url += f"&requestId={request_id}"
            upload_url += f"&dirIndexStr={entry['dirIndex']}"

            # POINT_ENTRY Requires offset
            if entry['type'] in ["0x4", "0x54"]:
                upload_url += f"&offset={entry['offset']}"

            # Upload file
            with open(entry['filename'], 'rb') as f:
                files = {"file": ("apifile.bin", f)}
                response = requests.post(upload_url, files=files, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Upload PSP entry failed. Status code: {response.status_code}. Reason: {response.reason}")

        self.logger.info("Upload PSP entries successful")

    def submit_psp_request(self, request_id: str, replacement_list: List[Dict[str, Any]],
                          sign_type: str = "NOSIGN", sign_hp: str = "0",
                          sign_username: Optional[str] = None, sign_password: Optional[str] = None,
                          sign_sp_function: str = "") -> None:
        """
        Submit PSP request

        Args:
            request_id: Request ID
            replacement_list: Replacement list
            sign_type: Sign type (NOSIGN 或 PK)
            sign_hp: Sign HP
            sign_username: Sign username
            sign_password: Sign password
            sign_sp_function: Sign SP function
        """
        self.logger.info("Submitting PSP Request...")

        # 使用預設Authentication資訊
        if sign_username is None:
            sign_username = self.username
        if sign_password is None:
            sign_password = self.password

        url = f"{self.base_url}api/bvmpsp/SubmitRequestAPI"
        url += f"?requestId={request_id}"
        url += f"&signType={sign_type}"
        url += f"&signHP={sign_hp}"
        url += f"&signUserName={sign_username}"
        url += f"&signPassword={sign_password}"
        url += f"&signSpFunction={sign_sp_function}"

        headers = {
            **self._get_auth_headers(),
            "Content-Type": "application/json"
        }

        # Update filename to BVM format
        submit_list = []
        for entry in replacement_list:
            entry_copy = entry.copy()
            entry_copy["filename"] = "BVM_apifile.bin"

            # Type 0x7 Special handling
            if entry["type"] == "0x7":
                entry_copy["filename"] = "RTMSignatureL1L2.bin"

            submit_list.append(entry_copy)

        response = requests.post(url, data=json.dumps(submit_list), headers=headers)

        if response.status_code == 200:
            self.logger.info("Submit PSP Request successful")
        else:
            raise Exception(f"Submit PSP Request failed. Status code: {response.status_code}. Reason: {response.reason}")

    def replace_psp_entries(self, replacement_list: List[Dict[str, Any]],
                           processor_name: Optional[str] = None,
                           platform_name: Optional[str] = None,
                           bios_type: Optional[str] = None,
                           revision: Optional[str] = None,
                           psp_config: Optional[str] = None,
                           purpose: Optional[str] = None,
                           sign_type: Optional[str] = None,
                           download_path: Optional[str] = None) -> str:
        """
        Complete PSP entry replacement workflow

        Args:
            replacement_list: Replacement list
            processor_name: Processor name (Optional，從Configuration讀取)
            platform_name: Platform name (Optional，從Configuration讀取)
            bios_type: BIOS type (Optional，從Configuration讀取)
            revision: 版本 (Required)
            psp_config: PSP Configuration (Optional，從Configuration讀取)
            purpose: Purpose (Optional，從Configuration讀取)
            sign_type: Sign type (Optional，從Configuration讀取)
            download_path: DownloadPath (Optional)

        Returns:
            Request ID
        """
        # 從Configuration讀取Default values
        if self.config:
            processor_name = processor_name or self.config.processor_name
            platform_name = platform_name or self.config.platform_name
            bios_type = bios_type or self.config.base_bios_type
            psp_config = psp_config or self.config.psp_config
            purpose = purpose or self.config.purpose
            sign_type = sign_type or self.config.sign_type

        # 檢查Required參數
        if not all([processor_name, platform_name, bios_type, revision, psp_config]):
            raise ValueError("Missing required parameters. Please provide or configure: processor_name, platform_name, bios_type, revision, psp_config")

        # 1. Generate request
        request_id = self.generate_psp_request(
            processor_name=processor_name,
            platform_name=platform_name,
            bios_type=bios_type,
            revision=revision,
            operation_type="PSP",
            purpose=purpose,
            psp_config=psp_config
        )

        # 2. Upload entries
        self.upload_psp_entries(request_id, replacement_list)

        # 3. Submit request
        sign_sp_function = ""
        if sign_type == "PK" and self.config:
            sign_sp_function = self.config.get("psp.signing.sp_function", "")

        self.submit_psp_request(
            request_id=request_id,
            replacement_list=replacement_list,
            sign_type=sign_type,
            sign_sp_function=sign_sp_function
        )

        # 4. Download (如果指定Path)
        if download_path:
            self.download_bios(request_id, download_path)

        return request_id


# ==================== Usage example ==================== #
if __name__ == "__main__":
    from bvm_config import BvmConfig

    print("=== PSP Replacement v2.0 Example ===\n")

    # Load configuration
    config = BvmConfig("bvm_config.yaml")
    replacer = PspReplacer(config=config)

    print(f"✓ Logged in as: {replacer.username}")
    print(f"✓ Platform: {config.platform_name}")
    print(f"✓ PSP Config: {config.psp_config}")
    print()

    # Example 1: Replace SMU firmware
    print("=== Example 1: Replace SMU Firmware ===")

    # 使用Configuration的Path
    smu_path = config.get_binary_path("SMU_46.59.0.bin")
    download_path = config.get_download_path("modified_bios.FD")

    replacement_list = [
        {
            "entryType": "IMAGE_ENTRY",
            "type": "0x8",              # SMU firmware
            "romId": "0x0",
            "instance": "0x0",
            "subProgram": "0x0",
            "operation": EntryOperationType.Modify.value,
            "filename": smu_path,
            "level": "0x2A",
            "dirIndex": "0x1",
            "detail": "Update SMU to 46.59.0",
            "isPspEntry": True
        }
    ]

    print(f"SMU Binary: {smu_path}")
    print(f"Download to: {download_path}")
    print()

    # Execute replacement (Commented out to avoid accidental execution)
    # request_id = replacer.replace_psp_entries(
    #     replacement_list=replacement_list,
    #     revision="TRM1004B_804_804",  # Specify version
    #     download_path=download_path
    # )
    # print(f"✓ Request ID: {request_id}")

    print("(Actual execution is commented, uncomment to run)")

    # Logout when done
    replacer.logout()
