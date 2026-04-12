# Entity Relationship Diagram

```mermaid
erDiagram
    USER {
        text id PK
        text username UK
        text email UK
        jsonb subscriptionFlags
        jsonb flags
        jsonb notificationFlags
    }
    POST {
        text id PK
        varchar type
        text sourceId FK
        text authorId FK
        boolean visible
        jsonb flags
    }
    SOURCE {
        text id PK
        varchar type
        text name
        text handle UK
        boolean active
        boolean private
    }
    COMMENT {
        varchar_14 id PK
        text postId FK
        varchar_36 userId FK
        varchar_14 parentId FK
        integer upvotes
        text content
    }
    FEED {
        text id PK
        text userId FK
    }
    SOURCE_MEMBER {
        text userId PK_FK
        text sourceId PK_FK
        varchar role
        text referralToken UK
    }
    BOOKMARK {
        text userId PK_FK
        text postId PK_FK
        text listId FK
        timestamp createdAt
    }
    USER_STREAK {
        text userId PK_FK
        integer currentStreak
        integer maxStreak
        timestamp lastViewAt
    }
    VIEW {
        text userId FK
        text postId FK
        timestamp timestamp
        boolean hidden
    }

    USER ||--o{ POST : "authors"
    SOURCE ||--o{ POST : "publishes"
    POST ||--o{ COMMENT : "has"
    USER ||--o{ COMMENT : "writes"
    COMMENT ||--o{ COMMENT : "replies to"
    USER ||--o{ FEED : "owns"
    USER ||--o{ SOURCE_MEMBER : "is member of"
    SOURCE ||--o{ SOURCE_MEMBER : "has members"
    USER ||--o{ BOOKMARK : "bookmarks"
    USER ||--|| USER_STREAK : "has streak"
```

**Source:** `.archeia/codebase/architecture/entities.json`
**Generated:** 2026-04-10
