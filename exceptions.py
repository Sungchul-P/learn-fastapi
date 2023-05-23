from typing import Optional

from fastapi import HTTPException, status


class UserCreationFailedException(HTTPException):
    def __init__(self, nickname: Optional[str]):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자({nickname}) 생성을 실패했습니다.",
        )


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"사용자를 찾을 수 없습니다.")


class UserAuthorizationFailedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=f"비밀번호가 틀렸습니다.")


class PostCreationFailedException(HTTPException):
    def __init__(self, title: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"게시글({title}) 생성을 실패했습니다."
        )


class PostNotFoundException(HTTPException):
    def __init__(self, post_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"번호 '{post_id}' 게시글을 찾을 수 없습니다."
        )


class PostAuthorizationFailedException(HTTPException):
    def __init__(self, author_id: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"{author_id}은(는) 해당 게시글에 대한 권한이 없습니다."
        )


class CommentCreationFailedException(HTTPException):
    def __init__(self, post_id: int):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"해당글({post_id})에 댓글 작성을 실패했습니다.",
        )


class CommentNotFoundException(HTTPException):
    def __init__(self, comment_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"번호 '{comment_id}' 댓글을 찾을 수 없습니다."
        )


class CommentAuthorizationFailedException(HTTPException):
    def __init__(self, author_id: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{author_id}은(는) 해당 댓글에 대한 권한이 부족하거나 비밀번호가 틀렸습니다.",
        )
