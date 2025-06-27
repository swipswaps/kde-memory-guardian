#!/usr/bin/env python3
"""
KDE Memory Guardian - Environment Management Script
Handles dependencies, environments, variables, folders, permissions

Features:
- Virtual environment management
- Dependency installation and verification
- Environment variable management
- Directory structure creation
- Permission management
- Service management
- Health checks
"""

import os
import sys
import subprocess
import json
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('environment_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnvironmentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.venv_path = self.project_root / "venv"
        self.config_file = self.project_root / ".env"
        self.requirements_file = self.project_root / "requirements.txt"
        
        # Environment configuration
        self.env_config = {
            'PROJECT_ROOT': str(self.project_root),
            'TESTING_DIR': str(self.project_root / "testing"),
            'DATABASE_TOOLS_DIR': str(self.project_root / "database-tools"),
            'LOGS_DIR': str(self.project_root / "logs"),
            'TEMP_DIR': "/tmp/kde-memory-guardian",
            'CRASH_ANALYZER_PORT': '9000',
            'DATABASE_MANAGER_PORT': '5000',
            'DEFAULT_CRASH_FILE': '/home/owner/Documents/2025_06_26_vcscode_crash.txt',
            'CLIPBOARD_DB_PATH': str(Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'),
            'GUARDIAN_DB_PATH': str(Path.home() / '.local/share/kde-memory-guardian/guardian.sqlite'),
            'PLAYWRIGHT_HEADLESS': 'false',
            'SELENIUM_HEADLESS': 'false',
            'TEST_TIMEOUT': '30',
            'AT_SPI_BUS_TYPE': 'session',
            'QT_ACCESSIBILITY': '1',
            'GTK_MODULES': 'gail:atk-bridge',
            'DISPLAY': ':0',
            'SUDO_TIMEOUT': '300',
            'TERMINAL_TIMEOUT': '30',
            'LOG_LEVEL': 'INFO',
            'DEBUG_MODE': 'false'
        }
        
        # Required directories
        self.required_dirs = [
            self.project_root / "logs",
            self.project_root / "temp",
            self.project_root / "data",
            self.project_root / "backups",
            self.project_root / "testing" / "screenshots",
            self.project_root / "testing" / "reports",
            self.project_root / "database-tools" / "logs",
            Path("/tmp/kde-memory-guardian"),
            Path.home() / ".local/share/kde-memory-guardian",
            Path.home() / ".config/kde-memory-guardian"
        ]
        
        # Required system packages
        self.system_packages = {
            'fedora': [
                'python3', 'python3-pip', 'python3-devel', 'gcc',
                'firefox', 'konsole', 'at-spi2-core', 'at-spi2-atk',
                'python3-gobject', 'dbus-x11', 'xdotool', 'wmctrl',
                'sqlite', 'curl', 'wget', 'git'
            ],
            'debian': [
                'python3', 'python3-pip', 'python3-dev', 'build-essential',
                'firefox', 'konsole', 'at-spi2-core', 'libatspi2.0-dev',
                'python3-gi', 'dbus-x11', 'xdotool', 'wmctrl',
                'sqlite3', 'curl', 'wget', 'git'
            ],
            'arch': [
                'python', 'python-pip', 'base-devel',
                'firefox', 'konsole', 'at-spi2-core', 'at-spi2-atk',
                'python-gobject', 'dbus', 'xdotool', 'wmctrl',
                'sqlite', 'curl', 'wget', 'git'
            ]
        }
    
    def detect_os(self) -> str:
        """Detect the operating system"""
        if shutil.which('dnf'):
            return 'fedora'
        elif shutil.which('apt'):
            return 'debian'
        elif shutil.which('pacman'):
            return 'arch'
        else:
            raise RuntimeError("Unsupported operating system")
    
    def create_directories(self) -> bool:
        """Create required directories with proper permissions"""
        logger.info("Creating directory structure...")
        
        try:
            for directory in self.required_dirs:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                
                # Set appropriate permissions
                if str(directory).startswith('/tmp'):
                    directory.chmod(0o1777)  # Sticky bit for temp dirs
                elif str(directory).startswith(str(Path.home())):
                    directory.chmod(0o700)   # Private user dirs
                else:
                    directory.chmod(0o755)   # Standard dirs
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False
    
    def install_system_packages(self) -> bool:
        """Install required system packages"""
        logger.info("Installing system packages...")
        
        try:
            os_type = self.detect_os()
            packages = self.system_packages[os_type]
            
            if os_type == 'fedora':
                cmd = ['sudo', 'dnf', 'install', '-y'] + packages
            elif os_type == 'debian':
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                cmd = ['sudo', 'apt', 'install', '-y'] + packages
            elif os_type == 'arch':
                cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("System packages installed successfully")
                return True
            else:
                logger.error(f"Failed to install system packages: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error installing system packages: {e}")
            return False
    
    def create_virtual_environment(self) -> bool:
        """Create and setup virtual environment"""
        logger.info("Setting up virtual environment...")
        
        try:
            if not self.venv_path.exists():
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)
                logger.info(f"Created virtual environment: {self.venv_path}")
            
            # Activate virtual environment and upgrade pip
            pip_path = self.venv_path / "bin" / "pip"
            subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        try:
            pip_path = self.venv_path / "bin" / "pip"
            
            if self.requirements_file.exists():
                subprocess.run([
                    str(pip_path), 'install', '-r', str(self.requirements_file)
                ], check=True)
            else:
                logger.warning("requirements.txt not found, installing basic dependencies")
                basic_deps = ['flask', 'playwright', 'selenium', 'requests', 'psutil']
                subprocess.run([str(pip_path), 'install'] + basic_deps, check=True)
            
            # Install Playwright browsers
            playwright_path = self.venv_path / "bin" / "playwright"
            if playwright_path.exists():
                subprocess.run([str(playwright_path), 'install', 'firefox'], check=True)
                subprocess.run([str(playwright_path), 'install', 'chromium'], check=True)
            
            logger.info("Python dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
    
    def setup_environment_variables(self) -> bool:
        """Setup environment variables"""
        logger.info("Setting up environment variables...")
        
        try:
            with open(self.config_file, 'w') as f:
                f.write(f"# KDE Memory Guardian Environment Configuration\n")
                f.write(f"# Generated on {datetime.now().isoformat()}\n\n")
                
                for key, value in self.env_config.items():
                    f.write(f"{key}={value}\n")
            
            # Set restrictive permissions on config file
            self.config_file.chmod(0o600)
            logger.info(f"Environment configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup environment variables: {e}")
            return False
    
    def setup_permissions(self) -> bool:
        """Setup file and directory permissions"""
        logger.info("Setting up permissions...")
        
        try:
            # Make scripts executable
            for script_path in self.project_root.rglob("*.sh"):
                script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            for script_path in self.project_root.rglob("*.py"):
                script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            # Setup sudo permissions for specific commands
            sudoers_content = f"""# KDE Memory Guardian sudo permissions
{os.getenv('USER')} ALL=(ALL) NOPASSWD: /usr/bin/journalctl, /usr/bin/dmesg
"""
            
            sudoers_file = "/etc/sudoers.d/kde-memory-guardian"
            try:
                with open('/tmp/kde-memory-guardian-sudoers', 'w') as f:
                    f.write(sudoers_content)
                
                subprocess.run([
                    'sudo', 'cp', '/tmp/kde-memory-guardian-sudoers', sudoers_file
                ], check=True)
                subprocess.run(['sudo', 'chmod', '440', sudoers_file], check=True)
                
                logger.info("Sudo permissions configured")
            except Exception as e:
                logger.warning(f"Could not setup sudo permissions: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup permissions: {e}")
            return False
    
    def verify_installation(self) -> Tuple[bool, List[str]]:
        """Verify the installation"""
        logger.info("Verifying installation...")
        
        issues = []
        
        # Check virtual environment
        if not self.venv_path.exists():
            issues.append("Virtual environment not found")
        
        # Check Python packages
        python_path = self.venv_path / "bin" / "python"
        if python_path.exists():
            required_packages = ['flask', 'playwright', 'selenium', 'requests']
            for package in required_packages:
                try:
                    subprocess.run([
                        str(python_path), '-c', f'import {package}'
                    ], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    issues.append(f"Python package {package} not available")
        else:
            issues.append("Python interpreter not found in virtual environment")
        
        # Check system commands
        required_commands = ['firefox', 'konsole', 'xdotool', 'wmctrl']
        for cmd in required_commands:
            if not shutil.which(cmd):
                issues.append(f"System command {cmd} not found")
        
        # Check directories
        for directory in self.required_dirs:
            if not directory.exists():
                issues.append(f"Required directory {directory} not found")
        
        # Check configuration
        if not self.config_file.exists():
            issues.append("Configuration file not found")
        
        success = len(issues) == 0
        if success:
            logger.info("✅ Installation verification successful")
        else:
            logger.error(f"❌ Installation verification failed with {len(issues)} issues")
            for issue in issues:
                logger.error(f"  - {issue}")
        
        return success, issues
    
    def run_health_check(self) -> Dict:
        """Run comprehensive health check"""
        logger.info("Running health check...")
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {}
        }
        
        # Check virtual environment
        health_status['checks']['virtual_environment'] = {
            'status': 'pass' if self.venv_path.exists() else 'fail',
            'details': f"Virtual environment at {self.venv_path}"
        }
        
        # Check system packages
        missing_commands = []
        for cmd in ['firefox', 'konsole', 'xdotool', 'wmctrl']:
            if not shutil.which(cmd):
                missing_commands.append(cmd)
        
        health_status['checks']['system_packages'] = {
            'status': 'pass' if not missing_commands else 'fail',
            'details': f"Missing commands: {missing_commands}" if missing_commands else "All commands available"
        }
        
        # Check directories
        missing_dirs = [str(d) for d in self.required_dirs if not d.exists()]
        health_status['checks']['directories'] = {
            'status': 'pass' if not missing_dirs else 'fail',
            'details': f"Missing directories: {missing_dirs}" if missing_dirs else "All directories exist"
        }
        
        # Check permissions
        config_readable = self.config_file.exists() and os.access(self.config_file, os.R_OK)
        health_status['checks']['permissions'] = {
            'status': 'pass' if config_readable else 'fail',
            'details': "Configuration file accessible" if config_readable else "Configuration file not accessible"
        }
        
        # Determine overall status
        all_checks = [check['status'] for check in health_status['checks'].values()]
        if all(status == 'pass' for status in all_checks):
            health_status['overall_status'] = 'healthy'
        elif any(status == 'pass' for status in all_checks):
            health_status['overall_status'] = 'degraded'
        else:
            health_status['overall_status'] = 'unhealthy'
        
        return health_status
    
    def setup_complete_environment(self) -> bool:
        """Setup complete environment"""
        logger.info("🚀 Starting complete environment setup...")
        
        steps = [
            ("Creating directories", self.create_directories),
            ("Installing system packages", self.install_system_packages),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Setting up environment variables", self.setup_environment_variables),
            ("Setting up permissions", self.setup_permissions),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Executing: {step_name}")
            if not step_func():
                logger.error(f"Failed at step: {step_name}")
                return False
        
        # Verify installation
        success, issues = self.verify_installation()
        if success:
            logger.info("🎉 Environment setup completed successfully!")
            
            # Print usage instructions
            logger.info("\n📋 Usage Instructions:")
            logger.info(f"1. Activate virtual environment: source {self.venv_path}/bin/activate")
            logger.info(f"2. Start crash analyzer: cd {self.project_root}/database-tools && python crash-analysis-correlator.py")
            logger.info(f"3. Run tests: cd {self.project_root}/testing && python end_to_end_comprehensive_tester.py")
            logger.info(f"4. Configuration file: {self.config_file}")
            
            return True
        else:
            logger.error("❌ Environment setup completed with issues")
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KDE Memory Guardian Environment Manager")
    parser.add_argument('--setup', action='store_true', help='Setup complete environment')
    parser.add_argument('--health-check', action='store_true', help='Run health check')
    parser.add_argument('--verify', action='store_true', help='Verify installation')
    
    args = parser.parse_args()
    
    manager = EnvironmentManager()
    
    if args.setup:
        success = manager.setup_complete_environment()
        sys.exit(0 if success else 1)
    elif args.health_check:
        health = manager.run_health_check()
        print(json.dumps(health, indent=2))
        sys.exit(0 if health['overall_status'] == 'healthy' else 1)
    elif args.verify:
        success, issues = manager.verify_installation()
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
