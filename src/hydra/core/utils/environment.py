"""
Environment utility for checking system requirements and tooling for Hydra.

This module provides functionality to verify that all necessary dependencies
and tools are available for Hydra to operate correctly.
"""

import subprocess
import shutil
import logging
import sys
import os
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    """Status of an environment check."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    """Result of an environment check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None


class EnvironmentChecker:
    """
    Utility class to check if the environment has all necessary tools
    and dependencies for Hydra to run properly.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results: List[CheckResult] = []
    
    def check_all(self) -> List[CheckResult]:
        """
        Run all environment checks and return results.
        
        Returns:
            List[CheckResult]: Results of all checks performed
        """
        self.results.clear()
        
        # Core system checks
        self._check_python_version()
        self._check_required_packages()
        
        # ROS2 checks
        self._check_ros2_installation()
        self._check_ros2_environment()
        self._check_ros2_packages()
        
        # Terminal emulator checks
        self._check_terminal_emulators()
        
        # Optional tool checks
        self._check_optional_tools()
        
        return self.results
    
    def print_summary(self) -> None:
        """Print a formatted summary of all check results."""
        print("\n" + "="*60)
        print("HYDRA ENVIRONMENT CHECK SUMMARY")
        print("="*60)
        
        pass_count = sum(1 for r in self.results if r.status == CheckStatus.PASS)
        fail_count = sum(1 for r in self.results if r.status == CheckStatus.FAIL)
        warn_count = sum(1 for r in self.results if r.status == CheckStatus.WARNING)
        skip_count = sum(1 for r in self.results if r.status == CheckStatus.SKIP)
        
        print(f"Total checks: {len(self.results)}")
        print(f"✅ Passed: {pass_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"⚠️  Warnings: {warn_count}")
        print(f"⏭️  Skipped: {skip_count}")
        print()
        
        # Show detailed results
        for result in self.results:
            icon = self._get_status_icon(result.status)
            print(f"{icon} {result.name}: {result.message}")
            
            if result.details:
                print(f"   Details: {result.details}")
            
            if result.suggestion:
                print(f"   💡 Suggestion: {result.suggestion}")
            print()
        
        # Overall assessment
        if fail_count == 0:
            print("🎉 All critical checks passed! Hydra should run correctly.")
        else:
            print("❗ Some critical checks failed. Please address the issues above.")
            
        if warn_count > 0:
            print("⚠️  Some warnings were found. Hydra may have limited functionality.")
    
    def _get_status_icon(self, status: CheckStatus) -> str:
        """Get appropriate icon for check status."""
        icons = {
            CheckStatus.PASS: "✅",
            CheckStatus.FAIL: "❌",
            CheckStatus.WARNING: "⚠️",
            CheckStatus.SKIP: "⏭️"
        }
        return icons.get(status, "❓")
    
    def _check_python_version(self) -> None:
        """Check if Python version meets requirements."""
        try:
            version = sys.version_info
            required_major, required_minor = 3, 12
            
            if version.major >= required_major and version.minor >= required_minor:
                self.results.append(CheckResult(
                    name="Python Version",
                    status=CheckStatus.PASS,
                    message=f"Python {version.major}.{version.minor}.{version.micro}"
                ))
            else:
                self.results.append(CheckResult(
                    name="Python Version",
                    status=CheckStatus.FAIL,
                    message=f"Python {version.major}.{version.minor}.{version.micro} (requires >= {required_major}.{required_minor})",
                    suggestion=f"Upgrade to Python {required_major}.{required_minor} or later"
                ))
        except Exception as e:
            self.results.append(CheckResult(
                name="Python Version",
                status=CheckStatus.FAIL,
                message="Could not determine Python version",
                details=str(e)
            ))
    
    def _check_required_packages(self) -> None:
        """Check if required Python packages are installed."""
        required_packages = ["yaml"]
        
        for package in required_packages:
            try:
                __import__(package)
                self.results.append(CheckResult(
                    name=f"Python Package: {package}",
                    status=CheckStatus.PASS,
                    message="Available"
                ))
            except ImportError:
                self.results.append(CheckResult(
                    name=f"Python Package: {package}",
                    status=CheckStatus.FAIL,
                    message="Not installed",
                    suggestion=f"Install with: pip install pyyaml"
                ))
    
    def _check_ros2_installation(self) -> None:
        """Check if ROS2 is installed and accessible."""
        try:
            result = subprocess.run(
                ["ros2", "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.results.append(CheckResult(
                    name="ROS2 Installation",
                    status=CheckStatus.PASS,
                    message=f"Found: {version}"
                ))
            else:
                self.results.append(CheckResult(
                    name="ROS2 Installation",
                    status=CheckStatus.FAIL,
                    message="ROS2 command failed",
                    details=result.stderr.strip(),
                    suggestion="Install ROS2 and ensure it's in your PATH"
                ))
                
        except FileNotFoundError:
            self.results.append(CheckResult(
                name="ROS2 Installation",
                status=CheckStatus.FAIL,
                message="ros2 command not found",
                suggestion="Install ROS2 and ensure it's in your PATH"
            ))
        except subprocess.TimeoutExpired:
            self.results.append(CheckResult(
                name="ROS2 Installation",
                status=CheckStatus.WARNING,
                message="ROS2 command timed out",
                suggestion="Check ROS2 installation"
            ))
        except Exception as e:
            self.results.append(CheckResult(
                name="ROS2 Installation",
                status=CheckStatus.FAIL,
                message="Error checking ROS2",
                details=str(e)
            ))
    
    def _check_ros2_environment(self) -> None:
        """Check if ROS2 environment is properly sourced."""
        required_vars = ["ROS_DISTRO", "ROS_VERSION"]
        
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                self.results.append(CheckResult(
                    name=f"ROS2 Environment: {var}",
                    status=CheckStatus.PASS,
                    message=f"{value}"
                ))
            else:
                self.results.append(CheckResult(
                    name=f"ROS2 Environment: {var}",
                    status=CheckStatus.WARNING,
                    message="Not set",
                    suggestion="Source your ROS2 setup script (e.g., source /opt/ros/humble/setup.bash)"
                ))
    
    def _check_ros2_packages(self) -> None:
        """Check if required ROS2 packages are available."""
        test_packages = ["turtlesim"]  # Packages used in examples
        
        for package in test_packages:
            try:
                result = subprocess.run(
                    ["ros2", "pkg", "list"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and package in result.stdout:
                    self.results.append(CheckResult(
                        name=f"ROS2 Package: {package}",
                        status=CheckStatus.PASS,
                        message="Available"
                    ))
                else:
                    self.results.append(CheckResult(
                        name=f"ROS2 Package: {package}",
                        status=CheckStatus.WARNING,
                        message="Not found",
                        suggestion=f"Install with: sudo apt install ros-$ROS_DISTRO-{package}"
                    ))
                    
            except Exception as e:
                self.results.append(CheckResult(
                    name=f"ROS2 Package: {package}",
                    status=CheckStatus.SKIP,
                    message="Could not check",
                    details=str(e)
                ))
    
    def _check_terminal_emulators(self) -> None:
        """Check if terminal emulators are available for interactive nodes."""
        terminals = [
            ("gnome-terminal", "GNOME Terminal"),
            ("xterm", "XTerm"),
            ("konsole", "KDE Konsole"),
            ("xfce4-terminal", "XFCE Terminal")
        ]
        
        found_terminals = []
        
        for cmd, name in terminals:
            if shutil.which(cmd):
                found_terminals.append(name)
        
        if found_terminals:
            self.results.append(CheckResult(
                name="Terminal Emulators",
                status=CheckStatus.PASS,
                message=f"Found: {', '.join(found_terminals)}"
            ))
        else:
            self.results.append(CheckResult(
                name="Terminal Emulators",
                status=CheckStatus.WARNING,
                message="No common terminal emulators found",
                suggestion="Install gnome-terminal, xterm, or konsole for interactive node support"
            ))
    
    def _check_optional_tools(self) -> None:
        """Check for optional tools that enhance functionality."""
        optional_tools = [
            ("rqt", "ROS2 GUI tools"),
            ("rviz2", "ROS2 visualization"),
            ("colcon", "ROS2 build tool")
        ]
        
        for tool, description in optional_tools:
            if shutil.which(tool):
                self.results.append(CheckResult(
                    name=f"Optional Tool: {tool}",
                    status=CheckStatus.PASS,
                    message=f"Available ({description})"
                ))
            else:
                self.results.append(CheckResult(
                    name=f"Optional Tool: {tool}",
                    status=CheckStatus.SKIP,
                    message=f"Not found ({description})",
                    suggestion=f"Install for enhanced functionality"
                ))
    
    def is_environment_ready(self) -> bool:
        """
        Check if environment is ready for Hydra operation.
        
        Returns:
            bool: True if all critical checks pass, False otherwise
        """
        if not self.results:
            self.check_all()
        
        # Consider environment ready if no critical failures
        critical_failures = [r for r in self.results if r.status == CheckStatus.FAIL]
        return len(critical_failures) == 0


def main():
    """Run environment check as a standalone script."""
    logging.basicConfig(level=logging.INFO)
    
    checker = EnvironmentChecker()
    checker.check_all()
    checker.print_summary()
    
    # Exit with appropriate code
    if checker.is_environment_ready():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()