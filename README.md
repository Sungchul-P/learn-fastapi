# learn-fastapi
FastAPI 사용법을 익히기 위한 레포지터리

## 초기 설정

```shell
pyenv local 3.9
poetry init --python ^3.9
poetry env use 3.9
poetry shell

poetry add fastapi
poetry add "uvicorn[standard]"
```

## 실행 및 API 테스트

```shell
uvicorn main:app --reload

# Swagger UI
http://127.0.0.1:8000/docs
```