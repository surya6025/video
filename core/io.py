"""
I/O operations for JarvisX
File management, sandboxing, and temporary artifacts
"""

import os
import shutil
import tempfile
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json
from datetime import datetime
from .logging_utils import get_logger

logger = get_logger(__name__)

class FileManager:
    """Manages file operations and temporary artifacts"""
    
    def __init__(self, temp_dir: str = "temp", max_temp_size: int = 100 * 1024 * 1024):  # 100MB
        self.temp_dir = Path(temp_dir)
        self.max_temp_size = max_temp_size
        self.safe_extensions = {
            '.txt', '.csv', '.json', '.xml', '.yaml', '.yml', '.md', '.log',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.pdf',
            '.py', '.js', '.html', '.css', '.sql', '.db', '.sqlite',
            '.zip', '.tar', '.gz', '.rar'
        }
        
        # Create temp directory
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.temp_dir / "models").mkdir(exist_ok=True)
        (self.temp_dir / "exports").mkdir(exist_ok=True)
        (self.temp_dir / "uploads").mkdir(exist_ok=True)
        (self.temp_dir / "charts").mkdir(exist_ok=True)
        (self.temp_dir / "reports").mkdir(exist_ok=True)
        
        logger.info(f"FileManager initialized with temp directory: {self.temp_dir}")
    
    def is_safe_file(self, file_path: str) -> bool:
        """Check if a file is safe to process"""
        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            
            # Check extension
            if extension not in self.safe_extensions:
                return False
            
            # Check if file exists and is readable
            if not path.exists() or not path.is_file():
                return False
            
            # Check file size
            if path.stat().st_size > self.max_temp_size:
                return False
            
            # Check if file is within temp directory or current working directory
            try:
                file_path = path.resolve()
                temp_path = self.temp_dir.resolve()
                cwd_path = Path.cwd().resolve()
                
                if not (file_path.is_relative_to(temp_path) or file_path.is_relative_to(cwd_path)):
                    return False
            except (ValueError, RuntimeError):
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking file safety: {e}")
            return False
    
    def create_temp_file(self, extension: str = ".tmp", prefix: str = "jarvisx_") -> Path:
        """Create a temporary file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}{timestamp}{extension}"
            temp_file = self.temp_dir / filename
            
            # Ensure unique filename
            counter = 1
            while temp_file.exists():
                filename = f"{prefix}{timestamp}_{counter}{extension}"
                temp_file = self.temp_dir / filename
                counter += 1
            
            # Create empty file
            temp_file.touch()
            logger.info(f"Created temp file: {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to create temp file: {e}")
            raise
    
    def create_temp_directory(self, prefix: str = "jarvisx_") -> Path:
        """Create a temporary directory"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dirname = f"{prefix}{timestamp}"
            temp_dir = self.temp_dir / dirname
            
            # Ensure unique directory name
            counter = 1
            while temp_dir.exists():
                dirname = f"{prefix}{timestamp}_{counter}"
                temp_dir = self.temp_dir / dirname
                counter += 1
            
            # Create directory
            temp_dir.mkdir()
            logger.info(f"Created temp directory: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to create temp directory: {e}")
            raise
    
    def save_file(self, content: Any, file_path: str, mode: str = "w") -> bool:
        """Save content to a file"""
        try:
            path = Path(file_path)
            
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save content
            if mode == "wb" or isinstance(content, bytes):
                with open(path, "wb") as f:
                    f.write(content)
            elif mode == "w":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(str(content))
            else:
                with open(path, mode) as f:
                    f.write(str(content))
            
            logger.info(f"Saved file: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save file {file_path}: {e}")
            return False
    
    def read_file(self, file_path: str, mode: str = "r") -> Optional[str]:
        """Read content from a file"""
        try:
            if not self.is_safe_file(file_path):
                logger.warning(f"Attempted to read unsafe file: {file_path}")
                return None
            
            path = Path(file_path)
            if mode == "rb":
                with open(path, "rb") as f:
                    return f.read()
            else:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file to a new location"""
        try:
            if not self.is_safe_file(source):
                logger.warning(f"Attempted to copy unsafe file: {source}")
                return False
            
            source_path = Path(source)
            dest_path = Path(destination)
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied file: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy file {source} to {destination}: {e}")
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move a file to a new location"""
        try:
            if not self.is_safe_file(source):
                logger.warning(f"Attempted to move unsafe file: {source}")
                return False
            
            source_path = Path(source)
            dest_path = Path(destination)
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved file: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file {source} to {destination}: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if not self.is_safe_file(file_path):
                logger.warning(f"Attempted to delete unsafe file: {file_path}")
                return False
            
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file"""
        try:
            if not self.is_safe_file(file_path):
                return None
            
            path = Path(file_path)
            stat = path.stat()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Calculate hash
            file_hash = self._calculate_file_hash(file_path)
            
            return {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "size_human": self._format_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "mime_type": mime_type or "unknown",
                "extension": path.suffix.lower(),
                "hash": file_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def list_temp_files(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """List temporary files matching a pattern"""
        try:
            files = []
            for file_path in self.temp_dir.rglob(pattern):
                if file_path.is_file():
                    file_info = self.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x["modified"], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Failed to list temp files: {e}")
            return []
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        try:
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            deleted_count = 0
            
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        if file_path.stat().st_mtime < cutoff_time:
                            file_path.unlink()
                            deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete old temp file {file_path}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} old temporary files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
            return 0
    
    def get_temp_directory_size(self) -> int:
        """Get total size of temporary directory"""
        try:
            total_size = 0
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception as e:
            logger.error(f"Failed to calculate temp directory size: {e}")
            return 0
    
    def export_file(self, source_path: str, export_name: str = None) -> Optional[str]:
        """Export a file to the exports directory"""
        try:
            if not self.is_safe_file(source_path):
                logger.warning(f"Attempted to export unsafe file: {source_path}")
                return None
            
            source = Path(source_path)
            
            if export_name is None:
                export_name = source.name
            
            # Ensure export name has proper extension
            if not export_name.endswith(source.suffix):
                export_name += source.suffix
            
            export_path = self.temp_dir / "exports" / export_name
            
            # Ensure unique export name
            counter = 1
            while export_path.exists():
                name, ext = export_path.stem, export_path.suffix
                export_path = self.temp_dir / "exports" / f"{name}_{counter}{ext}"
                counter += 1
            
            # Copy file to exports
            shutil.copy2(source, export_path)
            logger.info(f"Exported file: {source} -> {export_path}")
            
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Failed to export file {source_path}: {e}")
            return None

# Global file manager instance
file_manager = FileManager()