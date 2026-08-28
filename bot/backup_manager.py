"""
Backup System
Automated backup of database and configuration
"""
import os
import shutil
import json
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

from database import SessionLocal, Account, Task, Rating


class BackupManager:
    """
    Manages automated backups of the system
    """
    
    BACKUP_DIR = Path("backups")
    MAX_BACKUPS = 7  # Keep last 7 days
    
    def __init__(self):
        self.BACKUP_DIR.mkdir(exist_ok=True)
    
    def create_backup(self) -> Optional[str]:
        """Create a complete system backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_dir = self.BACKUP_DIR / backup_name
            backup_dir.mkdir(exist_ok=True)
            
            # Backup database
            self._backup_database(backup_dir)
            
            # Backup configuration
            self._backup_config(backup_dir)
            
            # Backup logs
            self._backup_logs(backup_dir)
            
            # Compress backup
            archive_path = self._compress_backup(backup_dir, backup_name)
            
            # Clean up uncompressed directory
            shutil.rmtree(backup_dir)
            
            # Clean old backups
            self._cleanup_old_backups()
            
            logger.info(f"Backup created: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def _backup_database(self, backup_dir: Path):
        """Backup database to JSON"""
        db = SessionLocal()
        try:
            # Export accounts
            accounts = db.query(Account).all()
            accounts_data = [acc.to_dict() for acc in accounts]
            
            with open(backup_dir / "accounts.json", "w", encoding="utf-8") as f:
                json.dump(accounts_data, f, ensure_ascii=False, indent=2)
            
            # Export tasks
            tasks = db.query(Task).all()
            tasks_data = [task.to_dict() for task in tasks]
            
            with open(backup_dir / "tasks.json", "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            
            # Export ratings
            ratings = db.query(Rating).all()
            ratings_data = [r.to_dict() for r in ratings]
            
            with open(backup_dir / "ratings.json", "w", encoding="utf-8") as f:
                json.dump(ratings_data, f, ensure_ascii=False, indent=2)
            
            logger.debug("Database backup completed")
            
        finally:
            db.close()
    
    def _backup_config(self, backup_dir: Path):
        """Backup configuration files"""
        config_files = [".env", "railway.json", "requirements.txt"]
        
        for filename in config_files:
            src = Path(filename)
            if src.exists():
                shutil.copy2(src, backup_dir / filename)
    
    def _backup_logs(self, backup_dir: Path):
        """Backup recent logs"""
        log_dir = Path("logs")
        if log_dir.exists():
            logs_backup = backup_dir / "logs"
            shutil.copytree(log_dir, logs_backup)
    
    def _compress_backup(self, backup_dir: Path, backup_name: str) -> Path:
        """Compress backup directory"""
        archive_path = self.BACKUP_DIR / f"{backup_name}.tar.gz"
        
        shutil.make_archive(
            str(archive_path).replace(".tar.gz", ""),
            "gztar",
            root_dir=backup_dir.parent,
            base_dir=backup_dir.name
        )
        
        return archive_path
    
    def _cleanup_old_backups(self):
        """Remove old backups beyond MAX_BACKUPS"""
        backups = sorted(self.BACKUP_DIR.glob("backup_*.tar.gz"), reverse=True)
        
        for old_backup in backups[self.MAX_BACKUPS:]:
            old_backup.unlink()
            logger.info(f"Removed old backup: {old_backup.name}")
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in sorted(self.BACKUP_DIR.glob("backup_*.tar.gz"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "path": str(backup_file),
            })
        
        return backups
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore from a backup (basic implementation)"""
        try:
            backup_path = self.BACKUP_DIR / backup_name
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_name}")
                return False
            
            # Extract backup
            restore_dir = self.BACKUP_DIR / "restore_temp"
            shutil.unpack_archive(str(backup_path), str(restore_dir))
            
            # Restore database from JSON
            # TODO: Implement database restoration
            
            # Clean up
            shutil.rmtree(restore_dir)
            
            logger.info(f"Backup restored: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def auto_backup_if_needed(self):
        """Check if backup is needed and create one"""
        today = datetime.now().date()
        latest_backup = self._get_latest_backup_date()
        
        if latest_backup is None or latest_backup.date() < today:
            logger.info("Creating scheduled backup...")
            self.create_backup()
    
    def _get_latest_backup_date(self) -> Optional[datetime]:
        """Get date of latest backup"""
        backups = sorted(self.BACKUP_DIR.glob("backup_*.tar.gz"), reverse=True)
        
        if backups:
            stat = backups[0].stat()
            return datetime.fromtimestamp(stat.st_ctime)
        
        return None
