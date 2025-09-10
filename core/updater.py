"""
Updater module for JarvisX
Handles self-update and rollback functionality
"""

import os
import json
import shutil
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
from core.io import FileManager

class UpdateManager:
    """Manages application updates and rollbacks"""
    
    def __init__(self, app_dir: str, temp_dir: str):
        self.app_dir = Path(app_dir)
        self.temp_dir = Path(temp_dir)
        self.backup_dir = self.app_dir / "backups"
        self.update_dir = self.temp_dir / "updates"
        self.manifest_file = self.app_dir / "update_manifest.json"
        
        # Ensure directories exist
        self.backup_dir.mkdir(exist_ok=True)
        self.update_dir.mkdir(exist_ok=True)
        
        self.file_manager = FileManager(str(self.temp_dir))
    
    def check_for_updates(self, update_url: str) -> Dict:
        """Check for available updates"""
        try:
            logger.info(f"Checking for updates from: {update_url}")
            
            # Get current version
            current_version = self._get_current_version()
            
            # Fetch update manifest
            response = requests.get(f"{update_url}/manifest.json", timeout=30)
            response.raise_for_status()
            
            manifest = response.json()
            latest_version = manifest.get('version')
            
            if not latest_version:
                raise ValueError("Invalid manifest: missing version")
            
            # Check if update is available
            if self._compare_versions(latest_version, current_version) > 0:
                logger.info(f"Update available: {current_version} -> {latest_version}")
                return {
                    'available': True,
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'changelog': manifest.get('changelog', ''),
                    'download_url': manifest.get('download_url', ''),
                    'size': manifest.get('size', 0),
                    'checksum': manifest.get('checksum', '')
                }
            else:
                logger.info("No updates available")
                return {
                    'available': False,
                    'current_version': current_version,
                    'latest_version': latest_version
                }
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def download_update(self, download_url: str, checksum: str) -> bool:
        """Download update package"""
        try:
            logger.info(f"Downloading update from: {download_url}")
            
            # Download update package
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            update_file = self.update_dir / "update.zip"
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum
            if not self._verify_checksum(update_file, checksum):
                raise ValueError("Checksum verification failed")
            
            logger.info("Update downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return False
    
    def install_update(self) -> bool:
        """Install the downloaded update"""
        try:
            logger.info("Installing update")
            
            # Create backup
            if not self._create_backup():
                raise RuntimeError("Failed to create backup")
            
            # Extract update
            update_file = self.update_dir / "update.zip"
            if not self._extract_update(update_file):
                raise RuntimeError("Failed to extract update")
            
            # Install files
            if not self._install_files():
                raise RuntimeError("Failed to install files")
            
            # Update manifest
            self._update_manifest()
            
            logger.info("Update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            # Attempt rollback
            self.rollback()
            return False
    
    def rollback(self) -> bool:
        """Rollback to previous version"""
        try:
            logger.info("Rolling back to previous version")
            
            # Find latest backup
            backup = self._find_latest_backup()
            if not backup:
                raise RuntimeError("No backup found")
            
            # Restore from backup
            if not self._restore_from_backup(backup):
                raise RuntimeError("Failed to restore from backup")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False
    
    def _get_current_version(self) -> str:
        """Get current application version"""
        try:
            from core import __version__
            return __version__
        except ImportError:
            return "0.1.0"
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings"""
        from packaging import version
        
        v1 = version.parse(version1)
        v2 = version.parse(version2)
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash == expected_checksum
        except Exception:
            return False
    
    def _create_backup(self) -> bool:
        """Create backup of current version"""
        try:
            timestamp = self._get_timestamp()
            backup_path = self.backup_dir / f"backup_{timestamp}"
            
            # Copy application files
            shutil.copytree(self.app_dir, backup_path, ignore=shutil.ignore_patterns(
                'backups', '__pycache__', '*.pyc', '*.pyo', '.git'
            ))
            
            # Save backup info
            backup_info = {
                'timestamp': timestamp,
                'version': self._get_current_version(),
                'path': str(backup_path)
            }
            
            backup_info_file = backup_path / "backup_info.json"
            with open(backup_info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def _extract_update(self, update_file: Path) -> bool:
        """Extract update package"""
        try:
            import zipfile
            
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(self.update_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Error extracting update: {e}")
            return False
    
    def _install_files(self) -> bool:
        """Install update files"""
        try:
            extracted_dir = self.update_dir / "jarvisx"
            if not extracted_dir.exists():
                raise RuntimeError("Update package structure invalid")
            
            # Copy new files
            for item in extracted_dir.iterdir():
                dest = self.app_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            
            return True
            
        except Exception as e:
            logger.error(f"Error installing files: {e}")
            return False
    
    def _update_manifest(self) -> bool:
        """Update installation manifest"""
        try:
            manifest = {
                'version': self._get_current_version(),
                'installed_at': self._get_timestamp(),
                'backup_created': True
            }
            
            with open(self.manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating manifest: {e}")
            return False
    
    def _find_latest_backup(self) -> Optional[Path]:
        """Find the most recent backup"""
        try:
            backups = list(self.backup_dir.glob("backup_*"))
            if not backups:
                return None
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x.name, reverse=True)
            return backups[0]
            
        except Exception as e:
            logger.error(f"Error finding latest backup: {e}")
            return None
    
    def _restore_from_backup(self, backup_path: Path) -> bool:
        """Restore application from backup"""
        try:
            # Remove current files (except backups and temp)
            for item in self.app_dir.iterdir():
                if item.name not in ['backups', 'temp', 'logs']:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # Restore from backup
            for item in backup_path.iterdir():
                if item.name not in ['backup_info.json']:
                    dest = self.app_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
            
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def cleanup(self):
        """Clean up temporary update files"""
        try:
            if self.update_dir.exists():
                shutil.rmtree(self.update_dir)
            logger.info("Update cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_update_history(self) -> List[Dict]:
        """Get update history"""
        try:
            history = []
            
            # Read manifest
            if self.manifest_file.exists():
                with open(self.manifest_file, 'r') as f:
                    manifest = json.load(f)
                    history.append(manifest)
            
            # Read backup info
            for backup_dir in self.backup_dir.glob("backup_*"):
                backup_info_file = backup_dir / "backup_info.json"
                if backup_info_file.exists():
                    with open(backup_info_file, 'r') as f:
                        backup_info = json.load(f)
                        history.append(backup_info)
            
            # Sort by timestamp
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return history
            
        except Exception as e:
            logger.error(f"Error getting update history: {e}")
            return []