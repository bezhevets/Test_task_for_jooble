from dataclasses import dataclass
from typing import List


@dataclass
class Property:
    link: str
    title: str
    region: str
    address: str
    description: str
    images: List[str]
    price: int
    rooms: int
    square: int
