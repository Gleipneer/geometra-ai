# Backup

Detta dokument beskriver hur man konfigurerar och hanterar backup för Geometra AI-systemet.

## Översikt

Backupsystemet innehåller:

1. **Databasbackup**
   - Redis
   - ChromaDB
   - PostgreSQL

2. **Filsystembackup**
   - Konfigurationsfiler
   - Loggfiler
   - Modeller

3. **Kodbackup**
   - Källkod
   - Dokumentation
   - Testdata

## Installation

1. Installera backupverktyg:
```bash
pip install boto3 azure-storage-blob google-cloud-storage
```

2. Skapa backupstruktur:
```bash
mkdir -p backup/{db,files,code}
```

## Konfiguration

### Databasbackup

1. Skapa `backup/db/redis.py`:
```python
"""Redis backup."""

import redis
import json
import os
from datetime import datetime
import boto3

class RedisBackup:
    """Redis backup manager."""
    
    def __init__(self, host: str, port: int, password: str):
        """Initialize backup manager."""
        self.redis = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('BACKUP_BUCKET')
    
    def backup(self) -> str:
        """Create backup."""
        # Get all keys
        keys = self.redis.keys('*')
        data = {}
        
        # Get values
        for key in keys:
            data[key] = self.redis.get(key)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'redis_backup_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f)
        
        # Upload to S3
        self.s3.upload_file(
            filename,
            self.bucket,
            f'redis/{filename}'
        )
        
        return filename
    
    def restore(self, filename: str):
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'redis/{filename}',
            filename
        )
        
        # Load data
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Restore to Redis
        for key, value in data.items():
            self.redis.set(key, value)
```

2. Skapa `backup/db/chroma.py`:
```python
"""ChromaDB backup."""

import chromadb
import os
from datetime import datetime
import boto3
import shutil

class ChromaBackup:
    """ChromaDB backup manager."""
    
    def __init__(self, persist_directory: str):
        """Initialize backup manager."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('BACKUP_BUCKET')
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'chroma_backup_{timestamp}'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy database files
        shutil.copytree(
            self.client.persist_directory,
            backup_dir,
            dirs_exist_ok=True
        )
        
        # Create archive
        archive = f'{backup_dir}.tar.gz'
        shutil.make_archive(
            backup_dir,
            'gztar',
            backup_dir
        )
        
        # Upload to S3
        self.s3.upload_file(
            archive,
            self.bucket,
            f'chroma/{archive}'
        )
        
        # Cleanup
        shutil.rmtree(backup_dir)
        os.remove(archive)
        
        return archive
    
    def restore(self, archive: str):
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'chroma/{archive}',
            archive
        )
        
        # Extract archive
        backup_dir = archive.replace('.tar.gz', '')
        shutil.unpack_archive(archive, backup_dir, 'gztar')
        
        # Restore database
        shutil.copytree(
            backup_dir,
            self.client.persist_directory,
            dirs_exist_ok=True
        )
        
        # Cleanup
        shutil.rmtree(backup_dir)
        os.remove(archive)
```

### Filsystembackup

1. Skapa `backup/files/config.py`:
```python
"""Configuration backup."""

import os
import json
from datetime import datetime
import boto3
import glob

class ConfigBackup:
    """Configuration backup manager."""
    
    def __init__(self, config_dir: str):
        """Initialize backup manager."""
        self.config_dir = config_dir
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('BACKUP_BUCKET')
    
    def backup(self) -> str:
        """Create backup."""
        # Get all config files
        config_files = glob.glob(f'{self.config_dir}/**/*.json', recursive=True)
        data = {}
        
        # Read files
        for file in config_files:
            with open(file, 'r') as f:
                data[file] = json.load(f)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'config_backup_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f)
        
        # Upload to S3
        self.s3.upload_file(
            filename,
            self.bucket,
            f'config/{filename}'
        )
        
        return filename
    
    def restore(self, filename: str):
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'config/{filename}',
            filename
        )
        
        # Load data
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Restore files
        for file, content in data.items():
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                json.dump(content, f, indent=2)
```

2. Skapa `backup/files/logs.py`:
```python
"""Log backup."""

import os
import glob
from datetime import datetime
import boto3
import shutil

class LogBackup:
    """Log backup manager."""
    
    def __init__(self, log_dir: str):
        """Initialize backup manager."""
        self.log_dir = log_dir
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('BACKUP_BUCKET')
    
    def backup(self) -> str:
        """Create backup."""
        # Get all log files
        log_files = glob.glob(f'{self.log_dir}/**/*.log', recursive=True)
        
        # Create backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'log_backup_{timestamp}'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy files
        for file in log_files:
            shutil.copy2(file, backup_dir)
        
        # Create archive
        archive = f'{backup_dir}.tar.gz'
        shutil.make_archive(
            backup_dir,
            'gztar',
            backup_dir
        )
        
        # Upload to S3
        self.s3.upload_file(
            archive,
            self.bucket,
            f'logs/{archive}'
        )
        
        # Cleanup
        shutil.rmtree(backup_dir)
        os.remove(archive)
        
        return archive
    
    def restore(self, archive: str):
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'logs/{archive}',
            archive
        )
        
        # Extract archive
        backup_dir = archive.replace('.tar.gz', '')
        shutil.unpack_archive(archive, backup_dir, 'gztar')
        
        # Restore files
        for file in glob.glob(f'{backup_dir}/**/*.log', recursive=True):
            shutil.copy2(file, self.log_dir)
        
        # Cleanup
        shutil.rmtree(backup_dir)
        os.remove(archive)
```

### Kodbackup

1. Skapa `backup/code/git.py`:
```python
"""Git backup."""

import os
from datetime import datetime
import boto3
import shutil

class GitBackup:
    """Git backup manager."""
    
    def __init__(self, repo_dir: str):
        """Initialize backup manager."""
        self.repo_dir = repo_dir
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('BACKUP_BUCKET')
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'code_backup_{timestamp}'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy repository
        shutil.copytree(
            self.repo_dir,
            backup_dir,
            dirs_exist_ok=True
        )
        
        # Create archive
        archive = f'{backup_dir}.tar.gz'
        shutil.make_archive(
            backup_dir,
            'gztar',
            backup_dir
        )
        
        # Upload to S3
        self.s3.upload_file(
            archive,
            self.bucket,
            f'code/{archive}'
        )
        
        # Cleanup
        shutil.rmtree(backup_dir)
        os.remove(archive)
        
        return archive
    
    def restore(self, archive: str):
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'code/{archive}',
            archive
        )
        
        # Extract archive
        backup_dir = archive.replace('.tar.gz', '')
        shutil.unpack_archive(archive, backup_dir, 'gztar')
        
        # Restore repository
        shutil.copytree(
            backup_dir,
            self.repo_dir,
            dirs_exist_ok=True
        )
        
        # Cleanup
        shutil.rmtree(backup_dir)
        os.remove(archive)
```

## Validering

1. Testa databasbackup:
```bash
python -m backup.db.redis
python -m backup.db.chroma
```

2. Testa filsystembackup:
```bash
python -m backup.files.config
python -m backup.files.logs
```

3. Testa kodbackup:
```bash
python -m backup.code.git
```

## Felsökning

### Backupproblem

1. **Databasproblem**
   - Kontrollera anslutningar
   - Verifiera behörigheter
   - Validera data

2. **Filsystemproblem**
   - Kontrollera diskutrymme
   - Verifiera filrättigheter
   - Validera filer

3. **Kodproblem**
   - Kontrollera Git-status
   - Verifiera ändringar
   - Validera arkiv

## Loggning

1. Konfigurera loggning i `backup/utils/logging.py`:
```python
"""Backup logging configuration."""

import logging
import os
from datetime import datetime

def setup_backup_logging():
    """Configure logging for backup."""
    log_dir = "logs/backup"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"backup_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
```

## Nästa steg

1. Konfigurera [DR](18_DR.md)
2. Skapa [Arkitekturdiagram](19_ARKITEKTURDIAGRAM.md)
3. Implementera [Monitoring](20_MONITORING.md) 