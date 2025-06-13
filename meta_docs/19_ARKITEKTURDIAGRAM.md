# Arkitekturdiagram

Detta dokument beskriver hur man skapar och underhåller arkitekturdiagram för Geometra AI-systemet.

## Översikt

Arkitekturdiagrammen innehåller:

1. **Systemdiagram**
   - Komponentdiagram
   - Sekvensdiagram
   - Deploymentdiagram

2. **Datadiagram**
   - ER-diagram
   - Datamodeller
   - Dataströmmar

3. **Infrastrukturdigram**
   - Nätverksdiagram
   - Säkerhetsdiagram
   - DR-diagram

## Installation

1. Installera diagramverktyg:
```bash
pip install graphviz plantuml pydot
```

2. Skapa diagramstruktur:
```bash
mkdir -p diagrams/{system,data,infrastructure}
```

## Konfiguration

### Systemdiagram

1. Skapa `diagrams/system/components.puml`:
```plantuml
@startuml
!theme plain
skinparam componentStyle rectangle

package "Frontend" {
    [React App] as frontend
    [Material-UI] as mui
    [Redux] as redux
}

package "Backend" {
    [FastAPI] as api
    [Redis] as redis
    [ChromaDB] as chroma
}

package "AI" {
    [GPT-4] as gpt4
    [GPT-3.5] as gpt35
    [Embeddings] as emb
}

frontend --> mui
frontend --> redux
frontend --> api
api --> redis
api --> chroma
api --> gpt4
api --> gpt35
api --> emb

@enduml
```

2. Skapa `diagrams/system/sequence.puml`:
```plantuml
@startuml
!theme plain
skinparam sequenceMessageAlign center

actor User
participant Frontend
participant Backend
participant AI
database Redis
database ChromaDB

User -> Frontend: Send message
Frontend -> Backend: POST /chat
Backend -> Redis: Get context
Backend -> ChromaDB: Get memory
Backend -> AI: Process message
AI --> Backend: Generate response
Backend -> Redis: Update context
Backend -> ChromaDB: Store memory
Backend --> Frontend: Return response
Frontend --> User: Display response

@enduml
```

3. Skapa `diagrams/system/deployment.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

node "Kubernetes Cluster" {
    node "Frontend Pod" {
        [React App]
        [Material-UI]
        [Redux]
    }
    
    node "Backend Pod" {
        [FastAPI]
        [Redis]
        [ChromaDB]
    }
    
    node "AI Pod" {
        [GPT-4]
        [GPT-3.5]
        [Embeddings]
    }
}

cloud "Cloud Storage" {
    [S3]
    [Backup]
}

database "Database" {
    [PostgreSQL]
}

@enduml
```

### Datadiagram

1. Skapa `diagrams/data/er.puml`:
```plantuml
@startuml
!theme plain
skinparam linetype ortho

entity "User" {
    * id : uuid
    --
    * username : string
    * email : string
    * password : string
    created_at : timestamp
    updated_at : timestamp
}

entity "Chat" {
    * id : uuid
    --
    * user_id : uuid
    * message : string
    * response : string
    created_at : timestamp
}

entity "Memory" {
    * id : uuid
    --
    * chat_id : uuid
    * content : string
    * embedding : vector
    created_at : timestamp
}

User ||--o{ Chat
Chat ||--o{ Memory

@enduml
```

2. Skapa `diagrams/data/models.puml`:
```plantuml
@startuml
!theme plain
skinparam classStyle rectangle

class User {
    +id: UUID
    +username: str
    +email: str
    +password: str
    +created_at: datetime
    +updated_at: datetime
}

class Chat {
    +id: UUID
    +user_id: UUID
    +message: str
    +response: str
    +created_at: datetime
}

class Memory {
    +id: UUID
    +chat_id: UUID
    +content: str
    +embedding: List[float]
    +created_at: datetime
}

User "1" -- "0..*" Chat
Chat "1" -- "0..*" Memory

@enduml
```

3. Skapa `diagrams/data/flows.puml`:
```plantuml
@startuml
!theme plain
skinparam linetype ortho

start
:User sends message;
:Backend receives message;
:Get context from Redis;
:Get memory from ChromaDB;
:Process with AI;
:Generate response;
:Update context in Redis;
:Store memory in ChromaDB;
:Return response;
:Frontend displays response;
stop

@enduml
```

### Infrastrukturdigram

1. Skapa `diagrams/infrastructure/network.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

cloud "Internet" {
    [Load Balancer]
}

node "VPC" {
    node "Public Subnet" {
        [API Gateway]
    }
    
    node "Private Subnet" {
        [Frontend]
        [Backend]
        [AI]
        [Redis]
        [ChromaDB]
    }
}

[Load Balancer] --> [API Gateway]
[API Gateway] --> [Frontend]
[API Gateway] --> [Backend]
[Backend] --> [AI]
[Backend] --> [Redis]
[Backend] --> [ChromaDB]

@enduml
```

2. Skapa `diagrams/infrastructure/security.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

cloud "Internet" {
    [WAF]
}

node "VPC" {
    node "Security Group" {
        [API Gateway]
        [Frontend]
        [Backend]
        [AI]
        [Redis]
        [ChromaDB]
    }
}

[WAF] --> [API Gateway]
[API Gateway] --> [Frontend]
[API Gateway] --> [Backend]
[Backend] --> [AI]
[Backend] --> [Redis]
[Backend] --> [ChromaDB]

@enduml
```

3. Skapa `diagrams/infrastructure/dr.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

cloud "Primary Region" {
    node "VPC" {
        [Frontend]
        [Backend]
        [AI]
        [Redis]
        [ChromaDB]
    }
}

cloud "DR Region" {
    node "VPC" {
        [Frontend]
        [Backend]
        [AI]
        [Redis]
        [ChromaDB]
    }
}

database "S3" {
    [Backup]
}

[Primary Region] --> [S3]
[DR Region] --> [S3]

@enduml
```

## Validering

1. Generera diagram:
```bash
plantuml diagrams/**/*.puml
```

2. Verifiera diagram:
```bash
python -m diagrams.validate
```

3. Uppdatera dokumentation:
```bash
python -m diagrams.update_docs
```

## Felsökning

### Diagramproblem

1. **Genereringsproblem**
   - Kontrollera PlantUML-syntax
   - Verifiera filer
   - Validera utdata

2. **Valideringsproblem**
   - Kontrollera strukturer
   - Verifiera relationer
   - Validera format

3. **Dokumentationsproblem**
   - Kontrollera länkar
   - Verifiera referenser
   - Validera innehåll

## Loggning

1. Konfigurera loggning i `diagrams/utils/logging.py`:
```python
"""Diagram logging configuration."""

import logging
import os
from datetime import datetime

def setup_diagram_logging():
    """Configure logging for diagrams."""
    log_dir = "logs/diagrams"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"diagrams_{datetime.now().strftime('%Y%m%d')}.log"
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

1. Implementera [Monitoring](20_MONITORING.md)
2. Konfigurera [Säkerhet](21_SÄKERHET.md)
3. Skapa [Dokumentation](22_DOKUMENTATION.md) 