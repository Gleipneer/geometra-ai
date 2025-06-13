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

3. **Infrastruktursdiagram**
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
  [WebSocket] as ws
  [Middleware] as middleware
}

package "AI" {
  [GPT-4] as gpt4
  [GPT-3.5] as gpt35
  [Memory] as memory
}

database "Redis" {
  [Cache] as cache
  [Session] as session
}

database "ChromaDB" {
  [Vector Store] as vector
  [Document Store] as doc
}

frontend --> api
api --> backend
backend --> ws
backend --> middleware
middleware --> gpt4
middleware --> gpt35
gpt4 --> memory
gpt35 --> memory
memory --> cache
memory --> session
memory --> vector
memory --> doc

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
participant Database

User -> Frontend: Send message
Frontend -> Backend: HTTP POST /chat
Backend -> AI: Process message
AI -> Database: Store context
Database --> AI: Context stored
AI --> Backend: Generate response
Backend --> Frontend: HTTP 200 OK
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
    [WebSocket]
  }
  
  node "AI Pod" {
    [GPT-4]
    [GPT-3.5]
  }
  
  database "Redis" {
    [Cache]
    [Session]
  }
  
  database "ChromaDB" {
    [Vector Store]
    [Document Store]
  }
}

cloud "Cloud Provider" {
  [Load Balancer]
  [Ingress]
  [Service Mesh]
}

[Load Balancer] --> [Ingress]
[Ingress] --> [Service Mesh]
[Service Mesh] --> [Frontend Pod]
[Service Mesh] --> [Backend Pod]
[Service Mesh] --> [AI Pod]

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
  password: String
  role: Enum
}

entity Chat {
  * id: UUID
  --
  * user_id: UUID
  * message: String
  timestamp: DateTime
  context: JSON
}

entity Memory {
  * id: UUID
  --
  * chat_id: UUID
  * content: String
  type: Enum
  metadata: JSON
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
  + id: UUID
  + username: String
  + email: String
  - password: String
  + role: Role
  + created_at: DateTime
  + updated_at: DateTime
  + authenticate()
  + authorize()
}

class Chat {
  + id: UUID
  + user_id: UUID
  + message: String
  + timestamp: DateTime
  + context: Dict
  + created_at: DateTime
  + updated_at: DateTime
  + process()
  + store()
}

class Memory {
  + id: UUID
  + chat_id: UUID
  + content: String
  + type: MemoryType
  + metadata: Dict
  + created_at: DateTime
  + updated_at: DateTime
  + store()
  + retrieve()
}

User "1" -- "0..*" Chat
Chat "1" -- "0..*" Memory

@enduml
```

3. Skapa `diagrams/data/flows.puml`:
```plantuml
@startuml
!theme plain
skinparam activityStyle rectangle

start
:Receive message;
:Validate input;
:Store in Redis;
:Process with GPT-4;
:Generate response;
:Store in ChromaDB;
:Return response;
stop

@enduml
```

### Infrastruktursdiagram

1. Skapa `diagrams/infrastructure/network.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

cloud "VPC" {
  node "Public Subnet" {
    [Load Balancer]
    [Ingress]
  }
  
  node "Private Subnet" {
    [Kubernetes Cluster]
    [Database Cluster]
  }
  
  node "Security Group" {
    [WAF]
    [Firewall]
  }
}

[Internet] --> [Load Balancer]
[Load Balancer] --> [Ingress]
[Ingress] --> [Kubernetes Cluster]
[Kubernetes Cluster] --> [Database Cluster]
[Security Group] --> [Load Balancer]
[Security Group] --> [Kubernetes Cluster]
[Security Group] --> [Database Cluster]

@enduml
```

2. Skapa `diagrams/infrastructure/security.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

node "Security" {
  node "Authentication" {
    [JWT]
    [OAuth2]
    [API Keys]
  }
  
  node "Authorization" {
    [RBAC]
    [ACL]
    [Policies]
  }
  
  node "Data Protection" {
    [Encryption]
    [Sanitization]
    [Validation]
  }
}

[Client] --> [JWT]
[Client] --> [OAuth2]
[Client] --> [API Keys]
[JWT] --> [RBAC]
[OAuth2] --> [RBAC]
[API Keys] --> [RBAC]
[RBAC] --> [ACL]
[ACL] --> [Policies]
[Policies] --> [Encryption]
[Policies] --> [Sanitization]
[Policies] --> [Validation]

@enduml
```

3. Skapa `diagrams/infrastructure/dr.puml`:
```plantuml
@startuml
!theme plain
skinparam nodeStyle rectangle

cloud "Primary Region" {
  node "Primary Cluster" {
    [Frontend]
    [Backend]
    [AI]
    [Database]
  }
}

cloud "DR Region" {
  node "DR Cluster" {
    [Frontend Replica]
    [Backend Replica]
    [AI Replica]
    [Database Replica]
  }
}

node "Replication" {
  [Database Replication]
  [File Replication]
  [Code Replication]
}

node "Failover" {
  [Automatic Failover]
  [Manual Failover]
  [Failback]
}

[Primary Cluster] --> [Database Replication]
[Database Replication] --> [DR Cluster]
[Primary Cluster] --> [File Replication]
[File Replication] --> [DR Cluster]
[Primary Cluster] --> [Code Replication]
[Code Replication] --> [DR Cluster]
[Primary Cluster] --> [Automatic Failover]
[Automatic Failover] --> [DR Cluster]
[Primary Cluster] --> [Manual Failover]
[Manual Failover] --> [DR Cluster]
[DR Cluster] --> [Failback]
[Failback] --> [Primary Cluster]

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
   - Kontrollera struktur
   - Verifiera länkar
   - Validera format

3. **Dokumentationsproblem**
   - Kontrollera referenser
   - Verifiera länkar
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

1. Implementera [Monitoring](26_MONITORING.md)
2. Konfigurera [Säkerhet](27_SÄKERHET.md)
3. Skapa [Dokumentation](28_DOKUMENTATION.md) 