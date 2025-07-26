"""
Core cleanup functionality for PostCodeMon project.
Removes testing artifacts, cache files, and other unnecessary files.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set, Dict, Any
import logging

# Use basic logging instead of the complex logger to avoid dependencies
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class PostCodeMonCleaner:
    """Core cleanup utility for PostCodeMon project files."""
    
    def __init__(self, project_root: str = None):
        """Initialize cleaner with project root directory."""
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.project_root = Path(project_root)
        
        # Define patterns for files/directories to clean
        self.cache_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
        ]
        
        self.test_patterns = [
            ".pytest_cache",
            ".coverage",
            "coverage.xml",
            "htmlcov",
            "*.cover",
            ".tox",
            ".nox",
        ]
        
        self.build_patterns = [
            "build",
            "dist",
            "*.egg-info",
            "*.egg",
            ".eggs",
        ]
        
        self.log_patterns = [
            "*.log",
            "*.tmp",
            "*.temp",
            "*.swp",
            "*.swo",
            "*~",
        ]
        
        self.ide_patterns = [
            ".vscode",
            ".idea",
            "*.sublime-project",
            "*.sublime-workspace",
        ]
    
    def find_files_to_clean(self, patterns: List[str]) -> Set[Path]:
        """Find all files matching the given patterns."""
        files_to_clean = set()
        
        for pattern in patterns:
            # Use glob to find matching files recursively
            matches = list(self.project_root.rglob(pattern))
            files_to_clean.update(matches)
        
        return files_to_clean
    
    def clean_cache_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean Python cache files."""
        files_to_clean = self.find_files_to_clean(self.cache_patterns)
        return self._remove_files(files_to_clean, "cache", dry_run)
    
    def clean_test_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean testing artifacts."""
        files_to_clean = self.find_files_to_clean(self.test_patterns)
        return self._remove_files(files_to_clean, "test", dry_run)
    
    def clean_build_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean build artifacts."""
        files_to_clean = self.find_files_to_clean(self.build_patterns)
        return self._remove_files(files_to_clean, "build", dry_run)
    
    def clean_log_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean log and temporary files."""
        files_to_clean = self.find_files_to_clean(self.log_patterns)
        return self._remove_files(files_to_clean, "log/temp", dry_run)
    
    def clean_ide_files(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean IDE-specific files."""
        files_to_clean = self.find_files_to_clean(self.ide_patterns)
        return self._remove_files(files_to_clean, "IDE", dry_run)
    
    def clean_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean all unnecessary files and return summary."""
        results = {
            'project_root': str(self.project_root),
            'dry_run': dry_run,
            'categories': {},
            'total_removed': 0,
            'errors': []
        }
        
        logger.info(f"Starting cleanup of PostCodeMon project at: {self.project_root}")
        
        # Clean each category
        categories = [
            ('cache', self.clean_cache_files),
            ('test', self.clean_test_files),
            ('build', self.clean_build_files),
            ('log', self.clean_log_files),
            ('ide', self.clean_ide_files)
        ]
        
        for category_name, clean_func in categories:
            try:
                category_result = clean_func(dry_run)
                results['categories'][category_name] = category_result
                results['total_removed'] += category_result['removed_count']
            except Exception as e:
                error_msg = f"Error cleaning {category_name} files: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        action_word = "Would remove" if dry_run else "Removed"
        logger.info(f"{action_word} {results['total_removed']} files/directories total")
        
        return results
    
    def _remove_files(self, files_to_clean: Set[Path], category: str, dry_run: bool = False) -> Dict[str, Any]:
        """Remove files and directories, returning detailed results."""
        result = {
            'category': category,
            'removed_count': 0,
            'files_removed': [],
            'errors': []
        }
        
        if not files_to_clean:
            logger.debug(f"No {category} files found to clean")
            return result
        
        action = "Would remove" if dry_run else "Removing"
        logger.info(f"{action} {len(files_to_clean)} {category} files")
        
        for file_path in sorted(files_to_clean):
            if not file_path.exists():
                continue
                
            try:
                # Make path relative to project root for logging
                relative_path = file_path.relative_to(self.project_root)
                logger.debug(f"  {relative_path}")
                
                if not dry_run:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                
                result['files_removed'].append(str(relative_path))
                result['removed_count'] += 1
                
            except Exception as e:
                error_msg = f"Error removing {file_path}: {e}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
        action_past = "would be removed" if dry_run else "removed"
        logger.info(f"  → {result['removed_count']} {category} files {action_past}")
        
        return result


def get_cleaner(project_root: str = None) -> PostCodeMonCleaner:
    """Factory function to create a PostCodeMonCleaner instance."""
    return PostCodeMonCleaner(project_root)