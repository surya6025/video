"""
Tests for the file I/O system
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from core.io import FileManager

class TestFileManager:
    """Test the FileManager class"""
    
    def test_init(self, temp_dir):
        """Test FileManager initialization"""
        manager = FileManager(temp_dir)
        assert manager.temp_dir == temp_dir
        assert os.path.exists(manager.temp_dir)
    
    def test_create_temp_file(self, temp_dir):
        """Test temporary file creation"""
        manager = FileManager(temp_dir)
        
        # Create temp file
        temp_file = manager.create_temp_file("test.txt")
        
        assert os.path.exists(temp_file)
        assert os.path.basename(temp_file).startswith("test_")
        assert temp_file.endswith(".txt")
        
        # Verify it's in temp directory
        assert os.path.dirname(temp_file) == temp_dir
    
    def test_create_temp_directory(self, temp_dir):
        """Test temporary directory creation"""
        manager = FileManager(temp_dir)
        
        # Create temp directory
        temp_dir_path = manager.create_temp_directory("test_dir")
        
        assert os.path.exists(temp_dir_path)
        assert os.path.isdir(temp_dir_path)
        assert os.path.basename(temp_dir_path).startswith("test_dir_")
        
        # Verify it's in temp directory
        assert os.path.dirname(temp_dir_path) == temp_dir
    
    def test_read_file_safe(self, temp_dir):
        """Test safe file reading"""
        manager = FileManager(temp_dir)
        
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Hello, World!")
        
        # Read file
        content = manager.read_file(test_file)
        assert content == "Hello, World!"
    
    def test_read_file_unsafe_path(self, temp_dir):
        """Test reading file with unsafe path"""
        manager = FileManager(temp_dir)
        
        # Try to read file outside temp directory
        unsafe_path = "/etc/passwd"
        
        with pytest.raises(ValueError):
            manager.read_file(unsafe_path)
    
    def test_write_file_safe(self, temp_dir):
        """Test safe file writing"""
        manager = FileManager(temp_dir)
        
        # Write file
        test_file = os.path.join(temp_dir, "test_write.txt")
        content = "Test content"
        manager.write_file(test_file, content)
        
        # Verify file was written
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            assert f.read() == content
    
    def test_write_file_unsafe_path(self, temp_dir):
        """Test writing file with unsafe path"""
        manager = FileManager(temp_dir)
        
        # Try to write file outside temp directory
        unsafe_path = "/tmp/unsafe.txt"
        
        with pytest.raises(ValueError):
            manager.write_file(unsafe_path, "content")
    
    def test_copy_file(self, temp_dir):
        """Test file copying"""
        manager = FileManager(temp_dir)
        
        # Create source file
        source_file = os.path.join(temp_dir, "source.txt")
        with open(source_file, 'w') as f:
            f.write("Source content")
        
        # Copy file
        dest_file = os.path.join(temp_dir, "dest.txt")
        manager.copy_file(source_file, dest_file)
        
        # Verify copy
        assert os.path.exists(dest_file)
        with open(dest_file, 'r') as f:
            assert f.read() == "Source content"
    
    def test_move_file(self, temp_dir):
        """Test file moving"""
        manager = FileManager(temp_dir)
        
        # Create source file
        source_file = os.path.join(temp_dir, "source_move.txt")
        with open(source_file, 'w') as f:
            f.write("Source content")
        
        # Move file
        dest_file = os.path.join(temp_dir, "dest_move.txt")
        manager.move_file(source_file, dest_file)
        
        # Verify move
        assert not os.path.exists(source_file)
        assert os.path.exists(dest_file)
        with open(dest_file, 'r') as f:
            assert f.read() == "Source content"
    
    def test_delete_file(self, temp_dir):
        """Test file deletion"""
        manager = FileManager(temp_dir)
        
        # Create test file
        test_file = os.path.join(temp_dir, "test_delete.txt")
        with open(test_file, 'w') as f:
            f.write("Delete me")
        
        # Delete file
        manager.delete_file(test_file)
        
        # Verify deletion
        assert not os.path.exists(test_file)
    
    def test_delete_directory(self, temp_dir):
        """Test directory deletion"""
        manager = FileManager(temp_dir)
        
        # Create test directory with files
        test_dir = os.path.join(temp_dir, "test_delete_dir")
        os.makedirs(test_dir)
        
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Delete me")
        
        # Delete directory
        manager.delete_directory(test_dir)
        
        # Verify deletion
        assert not os.path.exists(test_dir)
    
    def test_get_file_info(self, temp_dir):
        """Test getting file information"""
        manager = FileManager(temp_dir)
        
        # Create test file
        test_file = os.path.join(temp_dir, "test_info.txt")
        content = "Test content for info"
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Get file info
        info = manager.get_file_info(test_file)
        
        assert info['path'] == test_file
        assert info['size'] == len(content)
        assert info['exists'] is True
        assert 'hash' in info
        assert info['extension'] == '.txt'
    
    def test_get_file_info_nonexistent(self, temp_dir):
        """Test getting info for nonexistent file"""
        manager = FileManager(temp_dir)
        
        nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
        info = manager.get_file_info(nonexistent_file)
        
        assert info['path'] == nonexistent_file
        assert info['exists'] is False
        assert info['size'] == 0
    
    def test_list_files(self, temp_dir):
        """Test listing files in directory"""
        manager = FileManager(temp_dir)
        
        # Create test files
        files = ["file1.txt", "file2.txt", "file3.csv"]
        for filename in files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("content")
        
        # List files
        file_list = manager.list_files(temp_dir)
        
        assert len(file_list) >= len(files)
        for filename in files:
            assert any(os.path.basename(f) == filename for f in file_list)
    
    def test_cleanup_old_files(self, temp_dir):
        """Test cleanup of old temporary files"""
        manager = FileManager(temp_dir)
        
        # Create old temp files
        old_file = manager.create_temp_file("old.txt")
        old_dir = manager.create_temp_directory("old_dir")
        
        # Modify timestamps to make them old
        old_time = 1000000000  # Old timestamp
        os.utime(old_file, (old_time, old_time))
        os.utime(old_dir, (old_time, old_time))
        
        # Cleanup old files
        manager.cleanup_old_files(max_age_hours=1)
        
        # Verify old files were cleaned up
        assert not os.path.exists(old_file)
        assert not os.path.exists(old_dir)
    
    def test_safe_path_validation(self, temp_dir):
        """Test path safety validation"""
        manager = FileManager(temp_dir)
        
        # Safe paths
        safe_paths = [
            os.path.join(temp_dir, "file.txt"),
            os.path.join(temp_dir, "subdir", "file.txt"),
            os.path.join(temp_dir, "..", "..", "temp", "file.txt")  # Still within temp
        ]
        
        for path in safe_paths:
            assert manager._is_safe_path(path) is True
        
        # Unsafe paths
        unsafe_paths = [
            "/etc/passwd",
            "/home/user/file.txt",
            "/tmp/../etc/passwd",
            "C:\\Windows\\System32\\file.txt"
        ]
        
        for path in unsafe_paths:
            assert manager._is_safe_path(path) is False
    
    def test_file_extension_validation(self, temp_dir):
        """Test file extension validation"""
        manager = FileManager(temp_dir)
        
        # Safe extensions
        safe_extensions = ['.txt', '.csv', '.json', '.py', '.md']
        for ext in safe_extensions:
            assert manager._is_safe_extension(ext) is True
        
        # Unsafe extensions
        unsafe_extensions = ['.exe', '.bat', '.sh', '.ps1', '.vbs']
        for ext in unsafe_extensions:
            assert manager._is_safe_extension(ext) is False
    
    def test_file_hash_generation(self, temp_dir):
        """Test file hash generation"""
        manager = FileManager(temp_dir)
        
        # Create test file
        test_file = os.path.join(temp_dir, "test_hash.txt")
        content = "Test content for hashing"
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Get hash
        file_hash = manager._get_file_hash(test_file)
        
        assert isinstance(file_hash, str)
        assert len(file_hash) > 0
        
        # Hash should be consistent
        file_hash2 = manager._get_file_hash(test_file)
        assert file_hash == file_hash2
    
    def test_error_handling(self, temp_dir):
        """Test error handling in file operations"""
        manager = FileManager(temp_dir)
        
        # Test reading nonexistent file
        nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
        
        with pytest.raises(FileNotFoundError):
            manager.read_file(nonexistent_file)
        
        # Test writing to read-only directory
        read_only_dir = os.path.join(temp_dir, "readonly")
        os.makedirs(read_only_dir, mode=0o444)  # Read-only
        
        test_file = os.path.join(read_only_dir, "test.txt")
        
        with pytest.raises(PermissionError):
            manager.write_file(test_file, "content")
        
        # Cleanup
        os.chmod(read_only_dir, 0o755)
        shutil.rmtree(read_only_dir)
    
    def test_concurrent_access(self, temp_dir):
        """Test concurrent file access handling"""
        manager = FileManager(temp_dir)
        
        # Create multiple temp files simultaneously
        import threading
        
        def create_temp_file(thread_id):
            for i in range(5):
                temp_file = manager.create_temp_file(f"thread_{thread_id}_file_{i}.txt")
                with open(temp_file, 'w') as f:
                    f.write(f"Thread {thread_id}, file {i}")
        
        # Run multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_temp_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all files were created
        all_files = manager.list_files(temp_dir)
        assert len(all_files) >= 15  # 3 threads * 5 files each