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
   - Dataflöden

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
    [Redux Store] as store
    [API Client] as api
}

package "Backend" {
    [FastAPI] as backend
    [Auth Service] as auth
    [AI Service] as ai
}

package "Database" {
    [Redis] as redis
    [ChromaDB] as chroma
    [PostgreSQL] as postgres
}

frontend --> api
api --> backend
backend --> auth
backend --> ai
ai --> redis
ai --> chroma
backend --> postgres

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
database Database

User -> Frontend: Send message
Frontend -> Backend: API request
Backend -> AI: Process message
AI -> Database: Query context
Database --> AI: Return context
AI --> Backend: Generate response
Backend --> Frontend: API response
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
        [Nginx]
    }
    
    node "Backend Pod" {
        [FastAPI]
        [Gunicorn]
    }
    
    node "AI Pod" {
        [AI Service]
        [Model Server]
    }
    
    database "Redis" {
        [Cache]
        [Session]
    }
    
    database "ChromaDB" {
        [Vector Store]
    }
    
    database "PostgreSQL" {
        [User Data]
        [System Data]
    }
}

@enduml
```

### Datadiagram

1. Skapa `diagrams/data/er.puml`:
```plantuml
@startuml
!theme plain
skinparam classStyle rectangle

entity User {
    * id: UUID
    --
    * username: String
    * email: String
    * password: String
    created_at: DateTime
    updated_at: DateTime
}

entity Chat {
    * id: UUID
    --
    * user_id: UUID
    * title: String
    created_at: DateTime
    updated_at: DateTime
}

entity Message {
    * id: UUID
    --
    * chat_id: UUID
    * content: String
    * role: String
    created_at: DateTime
}

User ||--o{ Chat
Chat ||--o{ Message

@enduml
```

2. Skapa `diagrams/data/models.puml`:
```plantuml
@startuml
!theme plain
skinparam classStyle rectangle

class User {
    + id: UUID
    + username: String
    + email: String
    + password: String
    + created_at: DateTime
    + updated_at: DateTime
    --
    + authenticate()
    + update_profile()
}

class Chat {
    + id: UUID
    + user_id: UUID
    + title: String
    + created_at: DateTime
    + updated_at: DateTime
    --
    + add_message()
    + get_history()
}

class Message {
    + id: UUID
    + chat_id: UUID
    + content: String
    + role: String
    + created_at: DateTime
    --
    + format()
    + validate()
}

User "1" -- "many" Chat
Chat "1" -- "many" Message

@enduml
```

3. Skapa `diagrams/data/flows.puml`:
```plantuml
@startuml
!theme plain
skinparam activityStyle rectangle

start
:User sends message;
:Validate input;
:Query context;
:Generate response;
:Store message;
:Update chat history;
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
        [Application Servers]
        [Database Servers]
    }
    
    node "Security" {
        [WAF]
        [Security Groups]
    }
}

[Load Balancer] --> [API Gateway]
[API Gateway] --> [Application Servers]
[Application Servers] --> [Database Servers]

@enduml
```

2. Skapa `diagrams/infrastructure/security.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

node "Security Layers" {
    [WAF] as waf
    [API Gateway] as api
    [Application] as app
    [Database] as db
}

waf --> api
api --> app
app --> db

note right of waf
  DDoS protection
  Rate limiting
  IP filtering
end note

note right of api
  Authentication
  Authorization
  API key validation
end note

note right of app
  Input validation
  Data sanitization
  Session management
end note

note right of db
  Encryption
  Access control
  Audit logging
end note

@enduml
```

3. Skapa `diagrams/infrastructure/dr.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

node "Primary Region" {
    [Application]
    [Database]
    [Storage]
}

node "DR Region" {
    [Application]
    [Database]
    [Storage]
}

[Primary Region] <--> [DR Region] : Replication

note right of [Primary Region]
  Active
  Production
  Real-time
end note

note right of [DR Region]
  Standby
  Backup
  Recovery
end note

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
   - Verifiera filformat
   - Validera struktur

2. **Valideringsproblem**
   - Kontrollera länkar
   - Verifiera noder
   - Validera relationer

3. **Dokumentationsproblem**
   - Kontrollera referenser
   - Verifiera beskrivningar
   - Validera format

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

1. Implementera [Monitoring](32_MONITORING.md)
2. Konfigurera [Säkerhet](33_SÄKERHET.md)
3. Skapa [Dokumentation](34_DOKUMENTATION.md) 