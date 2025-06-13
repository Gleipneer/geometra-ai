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
import json
from datetime import datetime
from typing import Dict, Any

class RedisBackup:
    """Redis backup manager."""
    
    def __init__(self, host: str, port: int, password: str):
        """Initialize Redis backup."""
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
        # Get all keys
        keys = self.redis.keys('*')
        data = {}
        
        # Get values for each key
        for key in keys:
            data[key] = self.redis.get(key)
        
        # Create backup file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'redis_backup_{timestamp}.json'
        
        # Save to S3
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f'redis/{filename}',
            Body=json.dumps(data)
        )
        
        return filename
    
    def restore(self, filename: str) -> None:
        """Restore from backup."""
        # Get backup from S3
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=f'redis/{filename}'
        )
        data = json.loads(response['Body'].read())
        
        # Restore data
        for key, value in data.items():
            self.redis.set(key, value)
```

2. Skapa `backup/db/chroma.py`:
```python
"""ChromaDB backup."""

import chromadb
import boto3
import tarfile
import os
from datetime import datetime
from typing import List

class ChromaBackup:
    """ChromaDB backup manager."""
    
    def __init__(self, persist_directory: str):
        """Initialize ChromaDB backup."""
        self.persist_directory = persist_directory
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create archive
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'chroma_backup_{timestamp}.tar.gz'
        
        with tarfile.open(filename, 'w:gz') as tar:
            tar.add(self.persist_directory)
        
        # Upload to S3
        self.s3.upload_file(
            filename,
            self.bucket,
            f'chroma/{filename}'
        )
        
        # Clean up
        os.remove(filename)
        
        return filename
    
    def restore(self, filename: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'chroma/{filename}',
            filename
        )
        
        # Extract archive
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall()
        
        # Clean up
        os.remove(filename)
```

### Filsystembackup

1. Skapa `backup/files/config.py`:
```python
"""Configuration backup."""

import os
import boto3
import json
from datetime import datetime
from typing import Dict, Any

class ConfigBackup:
    """Configuration backup manager."""
    
    def __init__(self, config_dir: str):
        """Initialize config backup."""
        self.config_dir = config_dir
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Get all config files
        config_files = []
        for root, _, files in os.walk(self.config_dir):
            for file in files:
                if file.endswith('.json') or file.endswith('.yaml'):
                    config_files.append(os.path.join(root, file))
        
        # Create backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'config_backup_{timestamp}.json'
        
        data = {}
        for file in config_files:
            with open(file, 'r') as f:
                data[file] = f.read()
        
        # Save to S3
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f'config/{filename}',
            Body=json.dumps(data)
        )
        
        return filename
    
    def restore(self, filename: str) -> None:
        """Restore from backup."""
        # Get backup from S3
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=f'config/{filename}'
        )
        data = json.loads(response['Body'].read())
        
        # Restore files
        for file, content in data.items():
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, 'w') as f:
                f.write(content)
```

2. Skapa `backup/files/logs.py`:
```python
"""Log backup."""

import os
import boto3
import tarfile
from datetime import datetime
from typing import List

class LogBackup:
    """Log backup manager."""
    
    def __init__(self, log_dir: str):
        """Initialize log backup."""
        self.log_dir = log_dir
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create archive
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'log_backup_{timestamp}.tar.gz'
        
        with tarfile.open(filename, 'w:gz') as tar:
            tar.add(self.log_dir)
        
        # Upload to S3
        self.s3.upload_file(
            filename,
            self.bucket,
            f'logs/{filename}'
        )
        
        # Clean up
        os.remove(filename)
        
        return filename
    
    def restore(self, filename: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'logs/{filename}',
            filename
        )
        
        # Extract archive
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall()
        
        # Clean up
        os.remove(filename)
```

### Kodbackup

1. Skapa `backup/code/git.py`:
```python
"""Git backup."""

import os
import boto3
import tarfile
from datetime import datetime
from typing import List

class GitBackup:
    """Git backup manager."""
    
    def __init__(self, repo_dir: str):
        """Initialize git backup."""
        self.repo_dir = repo_dir
        self.s3 = boto3.client('s3')
        self.bucket = 'geometra-backups'
    
    def backup(self) -> str:
        """Create backup."""
        # Create archive
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'git_backup_{timestamp}.tar.gz'
        
        with tarfile.open(filename, 'w:gz') as tar:
            tar.add(self.repo_dir)
        
        # Upload to S3
        self.s3.upload_file(
            filename,
            self.bucket,
            f'git/{filename}'
        )
        
        # Clean up
        os.remove(filename)
        
        return filename
    
    def restore(self, filename: str) -> None:
        """Restore from backup."""
        # Download from S3
        self.s3.download_file(
            self.bucket,
            f'git/{filename}',
            filename
        )
        
        # Extract archive
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall()
        
        # Clean up
        os.remove(filename)
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

### Backup-problem

1. **Databasproblem**
   - Kontrollera anslutningar
   - Verifiera data
   - Validera format

2. **Filsystemproblem**
   - Kontrollera filrättigheter
   - Verifiera filer
   - Validera arkiv

3. **Kodproblem**
   - Kontrollera repository
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

1. Konfigurera [DR](24_DR.md)
2. Skapa [Arkitekturdiagram](25_ARKITEKTURDIAGRAM.md)
3. Implementera [Monitoring](26_MONITORING.md) 