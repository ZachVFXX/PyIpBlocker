import platform
import os
import tempfile
import logging
from typing import Union, List
import fire

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_hosts_path() -> str:
    system = platform.system()
    return r"C:\Windows\System32\drivers\etc\hosts" if system == "Windows" else "/etc/hosts"


class IpUtil(object):
    def __init__(self, LOOPBACK_IP: str = "127.0.0.1"):
        # Define the loopback IP to block or unblock addresses
        self._LOOPBACK_IP = LOOPBACK_IP

    def is_ip_blocked(self, ip: str, lines: List[str] | None = None) -> bool:
        entry = f"{self._LOOPBACK_IP} {ip}"
        if lines is None:
            with open(get_hosts_path(), "r") as hosts_file:
                lines = hosts_file.readlines()
        return any(entry in line for line in lines)

    def block_ip(self, target: Union[str, List[str]]) -> List[str]:
        if isinstance(target, str):
            target = [target]

        blocked_ips = []
        try:
            with open(get_hosts_path(), "r+") as hosts_file:
                lines = hosts_file.readlines()
                for ip in target:
                    if not self.is_ip_blocked(ip, lines):
                        hosts_file.write(f"\n{self._LOOPBACK_IP} {ip}")
                        blocked_ips.append(ip)
                        logging.info(f"Blocked {ip} in the host file.")
                    else:
                        logging.info(f"{ip} is already blocked in the host file.")
        except PermissionError:
            logging.error("Permission denied: Please run with elevated privileges.")
        except Exception as e:
            logging.error(f"An error occurred while blocking IPs: {e}")

        return blocked_ips

    def unblock_ip(self, list_of_target: Union[str, List[str]]) -> List[str]:
        if isinstance(list_of_target, str):
            list_of_target = [list_of_target]

        unblocked_ips = []
        try:
            with open(get_hosts_path(), "r") as hosts_file:
                lines = hosts_file.readlines()

            # Use a temporary file to avoid partial writes
            with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
                for line in lines:
                    if not any(f"{self._LOOPBACK_IP} {ip}" in line for ip in list_of_target):
                        temp_file.write(line)
                    else:
                        for ip in list_of_target:
                            if f"{self._LOOPBACK_IP} {ip}" in line:
                                unblocked_ips.append(ip)
                                logging.info(f"Unblocked {ip} from the host file.")

            # Replace the original hosts file with the updated one
            os.replace(temp_file.name, get_hosts_path())
        except PermissionError:
            logging.error("Permission denied: Please run with elevated privileges.")
        except Exception as e:
            logging.error(f"An error occurred while unblocking IPs: {e}")

        return unblocked_ips


if __name__ == "__main__":
    fire.Fire(IpUtil)