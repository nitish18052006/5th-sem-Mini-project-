from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    name: str
    email: str
    role: str = "user"
    eco_points: int = 0


@dataclass
class Report:
    id: int
    user_id: int
    title: str
    category: str
    description: str
    location: str
    severity: str
    priority_score: int
    status: str = "Submitted"
    image: Optional[str] = None


@dataclass
class AwarenessArticle:
    id: int
    title: str
    category: str
    summary: str
    content: str


@dataclass
class Challenge:
    id: int
    title: str
    description: str
    points: int
    difficulty: str = "Easy"