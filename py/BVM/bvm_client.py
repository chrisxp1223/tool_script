"""
BVM API Client - Shared Base Class

Provides common functionality for all BVM tools:
- Authentication and token management
- Processor/platform queries
- Base BIOS handling (Weekly/PI/User-Generated/By Request Id)
- Download functionality
"""

import json
import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    from bvm_config import BvmConfig

    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

# ==================== Constants ==================== #
BASE_URL = "http://bvm/"
VERSION = "2.00"

# ==================== Logging Configuration ==================== #
def setup_logging(log_file: str = "bvm_client.log", console_level: int = logging.INFO,
                  file_level: int = logging.DEBUG) -> logging.Logger:
    """
    Setup dual logging: console (main messages) + file (detailed debug)

    Args:
        log_file: Log file path
        console_level: Console log level (default: INFO - main messages only)
        file_level: File log level (default: DEBUG - all details)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Remove existing handlers
    logger.handlers.clear()

    # Console Handler - Main messages only (INFO and above)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)

    # File Handler - Detailed debug info
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Initialize default logger
logger = setup_logging()


class BvmClient:
    """BVM API Client Base Class

    Supports context manager for automatic logout:
        with BvmClient(config_file="config.yaml") as client:
            client.get_processor_list()
        # Automatically logged out
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[BvmConfig] = None,
        config_file: Optional[str] = None,
        log_file: Optional[str] = None,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
    ):
        """
        初始化 BVM 客戶端

        Args:
            username: BVM username (Optional if using config)
            password: BVM password (Optional if using config)
            base_url: BVM server URL (Default: http://bvm/)
            config: BvmConfig instance (Optional)
            config_file: Configuration file path (Optional)
            log_file: Log file path (Optional, default: bvm_client.log)
            console_level: Console log level (default: INFO - main messages only)
            file_level: File log level (default: DEBUG - detailed logs)

        Usage:
            # Method 1: Direct credentials
            client = BvmClient(username="user", password="pass")

            # Method 2: Using config file
            client = BvmClient(config_file="bvm_config.yaml")

            # Method 3: Using BvmConfig instance
            config = BvmConfig("bvm_config.yaml")
            client = BvmClient(config=config)

            # Method 4: Custom logging
            client = BvmClient(config_file="bvm_config.yaml",
                             log_file="my_app.log",
                             console_level=logging.WARNING)  # Only warnings on console
        """
        # Setup logging for this instance
        global logger
        # Always setup logging if custom levels are specified
        if log_file is not None or console_level != logging.INFO or file_level != logging.DEBUG:
            default_log = log_file if log_file else "bvm_client.log"
            logger = setup_logging(default_log, console_level, file_level)
        self.logger = logger
        # Load configuration
        if config is not None:
            self.config = config
        elif config_file is not None:
            if not HAS_CONFIG:
                raise ImportError(
                    "BvmConfig not available. Install PyYAML: pip install pyyaml"
                )
            self.config = BvmConfig(config_file)
        elif username is None and HAS_CONFIG:
            # Try to auto-load configuration
            try:
                self.config = BvmConfig()
            except FileNotFoundError:
                self.config = None
        else:
            self.config = None

        # Set authentication info
        if self.config is not None:
            self.base_url = base_url or self.config.base_url
            self.username = username or self.config.username
            self.password = password or self.config.password
        else:
            if username is None or password is None:
                raise ValueError(
                    "username and password are required when not using config"
                )
            self.base_url = base_url or BASE_URL
            self.username = username
            self.password = password

        self.token = None
        self.processor_list = None

        # Auto login
        self._login()

    # ==================== Authentication ==================== #

    def _login(self) -> None:
        """Login to BVM and get token"""
        logger.info("Logging in...")
        logger.debug(f"Login URL: {self.base_url}api/account/Login")
        logger.debug(f"Username: {self.username}")

        url = f"{self.base_url}api/account/Login"
        credentials = {"userName": self.username, "Password": self.password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(credentials))
        logger.debug(f"Login response status: {response.status_code}")

        if response.status_code == 200:
            self.token = response.json()["token"]
            logger.debug(f"Token received: {self.token[:20]}...")
            logger.info("Log in successful")
        elif response.status_code == 401:
            logger.error("Login failed: Invalid credentials")
            raise Exception("Log in failed. Please check your username and password.")
        else:
            logger.error(f"Login failed: {response.status_code} - {response.reason}")
            raise Exception(
                f"Log in failed. Status code: {response.status_code}. Reason: {response.reason}"
            )

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication header with token"""
        return {"Authorization": f"Bearer {self.token}"}

    def logout(self) -> None:
        """Logout from BVM and invalidate token"""
        if self.token is None:
            logger.debug("Already logged out")
            return

        logger.info("Logging out...")
        logger.debug(f"Logout URL: {self.base_url}api/account/Logout")
        url = f"{self.base_url}api/account/Logout"
        headers = self._get_auth_headers()

        try:
            response = requests.post(url, headers=headers)
            logger.debug(f"Logout response status: {response.status_code}")
            if response.status_code == 200:
                logger.info("Logout successful")
            else:
                logger.debug(f"Logout response: {response.status_code} (API may not support logout)")
        except Exception as e:
            logger.debug(f"Logout error (non-critical): {e}")
        finally:
            # Always clear token locally
            logger.debug("Clearing local token and cache")
            self.token = None
            self.processor_list = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically logout"""
        self.logout()
        return False

    # ==================== Processor/platform queries ==================== #

    def get_processor_list(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get processor list (Results will be cached)

        Args:
            force_refresh: Force refresh

        Returns:
            Processor list
        """
        if self.processor_list is not None and not force_refresh:
            logger.debug("Using cached processor list")
            return self.processor_list

        logger.debug("Fetching processor list from API...")
        url = f"{self.base_url}api/bvmmain/GetProcessorList"
        headers = self._get_auth_headers()

        response = requests.get(url, headers=headers)
        logger.debug(f"Processor list response status: {response.status_code}")

        if response.status_code == 200:
            self.processor_list = json.loads(response.text)
            logger.info(f"Retrieved {len(self.processor_list)} processors")
            return self.processor_list
        elif response.status_code == 401:
            logger.error("Get processor list failed: Invalid credentials")
            raise Exception("Get processor list failed. Please check your credential.")
        else:
            logger.error(f"Get processor list failed: {response.status_code} - {response.reason}")
            raise Exception(
                f"Get processor list failed. Status code: {response.status_code}. Reason: {response.reason}"
            )

    def get_processor_id(self, processor_name: str) -> Tuple[str, Dict[str, Any]]:
        """
        Find processor ID by name

        Args:
            processor_name: Processor name (For example: "Rembrandt - Family 19h")

        Returns:
            (processor_id, processor_dict)
        """
        processor_list = self.get_processor_list()

        for processor in processor_list:
            if processor["name"] == processor_name:
                return processor["id"], processor

        raise Exception(f"Processor not found: {processor_name}")

    def get_platform_id(
        self, processor: Dict[str, Any], platform_name: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Find platform ID by name

        Args:
            processor: Processor dictionary
            platform_name: Platform name (For example: "Rev_RMB_Mayan_Insyde_EDKII")

        Returns:
            (platform_id, platform_dict)
        """
        for platform in processor["platforms"]:
            if platform["name"] == platform_name:
                return platform["id"], platform

        raise Exception(f"Platform not found: {platform_name}")

    # ==================== Base BIOS handling ==================== #

    def get_weekly_bios_id(self, platform: Dict[str, Any], revision: str) -> str:
        """
        Find Weekly BIOS ID

        Args:
            platform: Platform dictionary
            revision: Version name (For example: "WXB4110N_312")

        Returns:
            Weekly BIOS ID
        """
        for weekly_bios in platform["weeklyBIOSes"]:
            if weekly_bios["name"] == revision:
                return weekly_bios["id"]

        raise Exception(f"Weekly BIOS not found: {revision}")

    def get_pi_bios_id(self, platform: Dict[str, Any], revision: str) -> str:
        """
        Find PI BIOS ID

        Args:
            platform: Platform dictionary
            revision: Version name (For example: "TXB0076C_313")

        Returns:
            PI BIOS ID
        """
        for pi_bios in platform["piBIOSes"]:
            if pi_bios["name"] == revision:
                return pi_bios["id"]

        raise Exception(f"PI BIOS not found: {revision}")

    def upload_user_gen_bios(self, bios_path: str) -> str:
        """
        Upload User-Generated BIOS

        Args:
            bios_path: BIOS File paths

        Returns:
            Uploaded BIOS ID
        """
        logger.info(f"Uploading BIOS: {bios_path}")
        logger.debug(f"Upload URL: {self.base_url}api/bvmmain/UploadBaseBIOS")
        url = f"{self.base_url}api/bvmmain/UploadBaseBIOS?name=filename"
        headers = self._get_auth_headers()

        with open(bios_path, "rb") as f:
            files = {"file": ("apibios.bin", f)}
            response = requests.post(url, files=files, headers=headers)

        logger.debug(f"Upload response status: {response.status_code}")
        if response.status_code == 200:
            bios_id = response.content.decode("ascii")
            logger.info(f"Upload successful (ID: {bios_id})")
            return bios_id
        else:
            logger.error(f"Upload failed: {response.status_code} - {response.reason}")
            raise Exception(
                f"Upload user-gen BIOS failed. Status code: {response.status_code}. Reason: {response.reason}"
            )

    def get_revision(
        self, platform: Dict[str, Any], bios_type: str, revision: str
    ) -> str:
        """
        Get revision ID based on BIOS type

        Args:
            platform: Platform dictionary
            bios_type: "Weekly BIOS" | "PI BIOS" | "User-Generated" | "By Request Id"
            revision: Version name or file path or Request ID

        Returns:
            Revision ID
        """
        if bios_type == "Weekly BIOS":
            return self.get_weekly_bios_id(platform, revision)
        elif bios_type == "PI BIOS":
            return self.get_pi_bios_id(platform, revision)
        elif bios_type == "User-Generated":
            return self.upload_user_gen_bios(revision)
        elif bios_type == "By Request Id":
            return revision
        else:
            raise Exception(f"Unknown BIOS type: {bios_type}")

    # ==================== Request management ==================== #

    def update_request_name(self, request_id: str, new_name: str) -> None:
        """
        Update request name

        Args:
            request_id: Request ID
            new_name: New name
        """
        logger.info("Updating name...")
        url = f"{self.base_url}api/bvmmain/UpdateNewName?requestId={request_id}&newName={new_name}"
        headers = self._get_auth_headers()

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            logger.info("Update name successful")
        else:
            raise Exception(
                f"Update name failed. Status code: {response.status_code}. Reason: {response.reason}"
            )

    # ==================== Download ==================== #

    def download_bios(self, request_id: str, download_path: str) -> None:
        """
        Download modified BIOS

        Args:
            request_id: Request ID
            download_path: Save path
        """
        logger.info(f"Downloading BIOS (Request: {request_id})...")
        logger.debug(f"Download URL: {self.base_url}api/bvmresult/DownloadBIOSByRequestId")
        logger.debug(f"Save path: {download_path}")
        url = f"{self.base_url}api/bvmresult/DownloadBIOSByRequestId?requestId={request_id}"

        response = requests.get(url)
        logger.debug(f"Download response status: {response.status_code}")

        if response.status_code == 200:
            file_size = len(response.content)
            with open(download_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded {file_size:,} bytes to: {download_path}")
        else:
            logger.error(f"Download failed: {response.status_code} - {response.reason}")
            raise Exception(
                f"Download BIOS failed. Status code: {response.status_code}. Reason: {response.reason}"
            )

    def download_tar(self, request_id: str, download_path: str) -> None:
        """
        Download complete tar file

        Args:
            request_id: Request ID
            download_path: Save path
        """
        logger.info(f"Downloading TAR (Request: {request_id})...")
        logger.debug(f"Download URL: {self.base_url}api/bvmresult/DownloadTarByRequestId")
        logger.debug(f"Save path: {download_path}")
        url = f"{self.base_url}api/bvmresult/DownloadTarByRequestId?requestId={request_id}"

        response = requests.get(url)
        logger.debug(f"Download response status: {response.status_code}")

        if response.status_code == 200:
            file_size = len(response.content)
            with open(download_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded {file_size:,} bytes to: {download_path}")
        else:
            raise Exception(
                f"Download Tar failed. Status code: {response.status_code}. Reason: {response.reason}"
            )


# ==================== Usage example ==================== #
if __name__ == "__main__":
    print("=== BVM Client Examples ===\n")

    # Method 1: Using config file (推薦)
    print("Method 1: Using config file")
    try:
        client = BvmClient(config_file="bvm_config.yaml")
        print(f"✓ Logged in as: {client.username}")
        print(f"✓ Base URL: {client.base_url}")

        # Get processor list
        processors = client.get_processor_list()
        print(f"✓ Found {len(processors)} processors")

        # Using config file中的Platform configuration
        if client.config:
            proc_id, proc = client.get_processor_id(client.config.processor_name)
            plat_id, plat = client.get_platform_id(proc, client.config.platform_name)
            print(f"✓ Processor ID: {proc_id}")
            print(f"✓ Platform ID: {plat_id}")

            # File paths example
            print(f"\n✓ Binary dir: {client.config.binary_dir}")
            print(f"✓ Download dir: {client.config.download_dir}")

        # Logout when done
        client.logout()

    except Exception as e:
        print(f"✗ Error: {e}")
