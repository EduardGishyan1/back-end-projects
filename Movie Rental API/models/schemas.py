"""Docstrings for User , Movie and Rental"""

from pydantic import BaseModel,EmailStr

class User(BaseModel):
    """Users BaseModel"""
    username: str
    password: str
    email: EmailStr

class Movie(BaseModel):
    """Movies BaseModel"""
    title: str
    genre: str
    rating: float

class Rental(BaseModel):
    """Rentals BaseModel"""
    user_id: int
    movie_id: int
    rental_duration: float   
