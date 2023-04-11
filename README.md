# learn-fastapi
FastAPI 사용법을 익히기 위한 레포지터리

## 요구 사항

- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation) 1.4.0+

## 패키지 설치 및 가상 환경 실행

```shell
poetry install
poetry shell

# 코드 일관성을 위해 pre-commit 훅 스크립트 설치
pre-commit install
```

## 실행 및 API 테스트

```shell
uvicorn main:app --reload

# Swagger UI
http://127.0.0.1:8000/docs
```

## 레이어드 아키텍쳐

```mermaid
graph TB
    subgraph Main
        MAIN[main.py]
    end
    subgraph API Layer
        API[api.py]
    end
    subgraph Service Layer
        SVC[service.py]
    end
    subgraph Domain Layer
        ENT[model.py]
    end
    subgraph Data Access Layer
        DB[database.py]
    end
    MAIN --> API
    MAIN --> DB
    API --> SVC
    SVC --> ENT
```

## GitHub Flow 브랜치 전략 프로세스

1. 브랜치 생성 (네이밍 컨벤션 : feature/add-logic)
2. 코드 커밋 & 푸시
3. PR(Pull Request) 생성 후, 테스트 및 리뷰
4. 병합(Merge) 및 배포(Deploy)
5. 병합 및 배포 완료 된 브랜치는 삭제 

```mermaid
graph LR
    A[main] -- Feature --> B[feature/feature-1]
    A -- Feature --> C[feature/feature-2]
    B -- Pull Request --> D[test, review]
    C -- Pull Request --> E[test, review]
    D -- Merge --> A
    E -- Merge --> A
```

## Entity Relationship Diagrams

```mermaid
erDiagram
    POST {
        int id PK "게시글 아이디"
        string title 
        string content
        string author_id FK "작성자 아이디"
    }
    
    USER {
        string id PK "작성자 아이디"
        string password 
        string nickname
        datetime created_at "생성 날짜"
    }
    
    COMMENT {
        int id PK "댓글 아이디"
        string author_id FK "작성자 아이디"
        int post_id FK "게시글 아이디"
        string content
        datetime created_at "생성 날짜"
    }
    
    POST ||--o{ COMMENT : contains
    USER ||--o{ POST : create
    USER ||--o{ COMMENT : create
```