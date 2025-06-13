from pathlib import Path

BACKUP_DIR = Path("backup")
DB_BACKUP_DIR = BACKUP_DIR / "db"
FILES_BACKUP_DIR = BACKUP_DIR / "files"
CODE_BACKUP_DIR = BACKUP_DIR / "code"

def setup_backup():
    """Setup backup directories."""
    for directory in [BACKUP_DIR, DB_BACKUP_DIR, FILES_BACKUP_DIR, CODE_BACKUP_DIR]:
        directory.mkdir(exist_ok=True)
