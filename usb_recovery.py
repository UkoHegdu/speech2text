"""Auto-recovery for the USB mic dropping out behind the Dell monitor's hub chain.

Restarting the hub requires admin rights (pnputil /restart-device), so the actual
restart runs via a pre-registered Scheduled Task (Speech2Text_USBRecover, created
once with "run with highest privileges") instead of elevating this process directly.
"""

import subprocess

TASK_NAME = "Speech2Text_USBRecover"


def trigger() -> bool:
    """Ask the scheduled task to restart the webcam's USB hub. Returns True if triggered."""
    try:
        subprocess.run(
            ["schtasks", "/run", "/tn", TASK_NAME],
            check=True,
            capture_output=True,
            timeout=10,
        )
        return True
    except Exception:
        return False
