from typing import Dict, Optional
from models import InMemoryCodeReview
from datetime import datetime
import threading

class InMemoryStorage:
    """인메모리 저장소 클래스"""
    
    def __init__(self):
        self._storage: Dict[str, InMemoryCodeReview] = {}
        self._lock = threading.Lock()
    
    def create_review(self, review_id: str, user_id: str = "default") -> InMemoryCodeReview:
        """새로운 코드 리뷰 생성"""
        with self._lock:
            review = InMemoryCodeReview(
                id=review_id,
                user_id=user_id,
                status="processing",
                created_at=datetime.utcnow()
            )
            self._storage[review_id] = review
            return review
    
    def get_review(self, review_id: str) -> Optional[InMemoryCodeReview]:
        """코드 리뷰 조회"""
        with self._lock:
            return self._storage.get(review_id)
    
    def update_review(self, review_id: str, **kwargs) -> Optional[InMemoryCodeReview]:
        """코드 리뷰 업데이트"""
        with self._lock:
            review = self._storage.get(review_id)
            if review:
                # Pydantic 모델의 copy 메서드 사용하여 업데이트
                updated_data = review.dict()
                updated_data.update(kwargs)
                self._storage[review_id] = InMemoryCodeReview(**updated_data)
                return self._storage[review_id]
            return None
    
    def delete_review(self, review_id: str) -> bool:
        """코드 리뷰 삭제"""
        with self._lock:
            if review_id in self._storage:
                del self._storage[review_id]
                return True
            return False
    
    def list_reviews(self, user_id: Optional[str] = None) -> list:
        """코드 리뷰 목록 조회"""
        with self._lock:
            reviews = list(self._storage.values())
            if user_id:
                reviews = [r for r in reviews if r.user_id == user_id]
            return reviews
    
    def clear_all(self):
        """모든 데이터 삭제 (테스트용)"""
        with self._lock:
            self._storage.clear()

# 전역 저장소 인스턴스
storage = InMemoryStorage()