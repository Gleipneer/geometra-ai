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
import boto3
from datetime import datetime
import os

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
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        backup_dir = f"backup/db/redis/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup all keys
        for key in self.redis.keys():
            value = self.redis.get(key)
            with open(f"{backup_dir}/{key}", 'w') as f:
                f.write(value)
        
        # Upload to S3
        self.s3.upload_file(
            f"{backup_dir}.tar.gz",
            self.bucket,
            f"redis/{os.path.basename(backup_dir)}.tar.gz"
        )
        
        return backup_dir
    
    def restore(self, backup_path: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f"redis/{os.path.basename(backup_path)}.tar.gz",
            f"{backup_path}.tar.gz"
        )
        
        # Restore keys
        for key_file in os.listdir(backup_path):
            with open(f"{backup_path}/{key_file}", 'r') as f:
                value = f.read()
            self.redis.set(key_file, value)
```

2. Skapa `backup/db/chroma.py`:
```python
"""ChromaDB backup."""

import chromadb
import boto3
from datetime import datetime
import os

class ChromaBackup:
    """ChromaDB backup manager."""
    
    def __init__(self, host: str, port: int):
        """Initialize backup manager."""
        self.client = chromadb.HttpClient(host=host, port=port)
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        backup_dir = f"backup/db/chroma/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup collections
        for collection in self.client.list_collections():
            data = collection.get()
            with open(f"{backup_dir}/{collection.name}.json", 'w') as f:
                f.write(data)
        
        # Upload to S3
        self.s3.upload_file(
            f"{backup_dir}.tar.gz",
            self.bucket,
            f"chroma/{os.path.basename(backup_dir)}.tar.gz"
        )
        
        return backup_dir
    
    def restore(self, backup_path: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f"chroma/{os.path.basename(backup_path)}.tar.gz",
            f"{backup_path}.tar.gz"
        )
        
        # Restore collections
        for collection_file in os.listdir(backup_path):
            with open(f"{backup_path}/{collection_file}", 'r') as f:
                data = f.read()
            self.client.create_collection(
                name=collection_file.replace('.json', ''),
                data=data
            )
```

### Filsystembackup

1. Skapa `backup/files/config.py`:
```python
"""Configuration backup."""

import boto3
from datetime import datetime
import os
import tarfile

class ConfigBackup:
    """Configuration backup manager."""
    
    def __init__(self):
        """Initialize backup manager."""
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        backup_dir = f"backup/files/config/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup config files
        config_files = [
            '.env',
            'config.yaml',
            'logging.yaml'
        ]
        
        for file in config_files:
            if os.path.exists(file):
                with open(file, 'r') as src, open(f"{backup_dir}/{file}", 'w') as dst:
                    dst.write(src.read())
        
        # Create archive
        with tarfile.open(f"{backup_dir}.tar.gz", 'w:gz') as tar:
            tar.add(backup_dir)
        
        # Upload to S3
        self.s3.upload_file(
            f"{backup_dir}.tar.gz",
            self.bucket,
            f"config/{os.path.basename(backup_dir)}.tar.gz"
        )
        
        return backup_dir
    
    def restore(self, backup_path: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f"config/{os.path.basename(backup_path)}.tar.gz",
            f"{backup_path}.tar.gz"
        )
        
        # Extract archive
        with tarfile.open(f"{backup_path}.tar.gz", 'r:gz') as tar:
            tar.extractall()
        
        # Restore files
        for file in os.listdir(backup_path):
            with open(f"{backup_path}/{file}", 'r') as src, open(file, 'w') as dst:
                dst.write(src.read())
```

2. Skapa `backup/files/logs.py`:
```python
"""Log backup."""

import boto3
from datetime import datetime
import os
import tarfile

class LogBackup:
    """Log backup manager."""
    
    def __init__(self):
        """Initialize backup manager."""
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        backup_dir = f"backup/files/logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup log files
        log_dir = 'logs'
        if os.path.exists(log_dir):
            for root, _, files in os.walk(log_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(backup_dir, file)
                    with open(src_path, 'r') as src, open(dst_path, 'w') as dst:
                        dst.write(src.read())
        
        # Create archive
        with tarfile.open(f"{backup_dir}.tar.gz", 'w:gz') as tar:
            tar.add(backup_dir)
        
        # Upload to S3
        self.s3.upload_file(
            f"{backup_dir}.tar.gz",
            self.bucket,
            f"logs/{os.path.basename(backup_dir)}.tar.gz"
        )
        
        return backup_dir
    
    def restore(self, backup_path: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f"logs/{os.path.basename(backup_path)}.tar.gz",
            f"{backup_path}.tar.gz"
        )
        
        # Extract archive
        with tarfile.open(f"{backup_path}.tar.gz", 'r:gz') as tar:
            tar.extractall()
        
        # Restore files
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        for file in os.listdir(backup_path):
            with open(f"{backup_path}/{file}", 'r') as src, open(f"{log_dir}/{file}", 'w') as dst:
                dst.write(src.read())
```

### Kodbackup

1. Skapa `backup/code/git.py`:
```python
"""Git backup."""

import boto3
from datetime import datetime
import os
import subprocess

class GitBackup:
    """Git backup manager."""
    
    def __init__(self):
        """Initialize backup manager."""
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create backup directory
        backup_dir = f"backup/code/git/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create git bundle
        bundle_file = f"{backup_dir}/repo.bundle"
        subprocess.run([
            'git', 'bundle', 'create', bundle_file, '--all'
        ])
        
        # Upload to S3
        self.s3.upload_file(
            bundle_file,
            self.bucket,
            f"git/{os.path.basename(backup_dir)}.bundle"
        )
        
        return backup_dir
    
    def restore(self, backup_path: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f"git/{os.path.basename(backup_path)}.bundle",
            f"{backup_path}/repo.bundle"
        )
        
        # Clone from bundle
        subprocess.run([
            'git', 'clone', f"{backup_path}/repo.bundle", '.'
        ])
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
   - Verifiera autentisering
   - Validera data

2. **Filsystemproblem**
   - Kontrollera filrättigheter
   - Verifiera diskutrymme
   - Validera filformat

3. **Kodproblem**
   - Kontrollera repository
   - Verifiera branches
   - Validera commits

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

1. Konfigurera [DR](30_DR.md)
2. Skapa [Arkitekturdiagram](31_ARKITEKTURDIAGRAM.md)
3. Implementera [Monitoring](32_MONITORING.md) 