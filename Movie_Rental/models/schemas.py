from pydantic import BaseModel,EmailStr

class User(BaseModel):
    username:str
    password:str
    email:str
    
class Movie(BaseModel):
    title:str
    genre:str
    rating:float
    
class Rental(BaseModel):
    user:str
    movie:str
    rental_duration:float