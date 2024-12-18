from fastapi import FastAPI
import uvicorn
from routers import auth,movies,rentals

app = FastAPI()

app.include_router(auth.users_router)
app.include_router(movies.movies_router)
app.include_router(rentals.rentals_router)

if __name__ == "__main__":
    uvicorn.run("main:app",port = 3001,reload = True)