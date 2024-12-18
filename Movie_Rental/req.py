import requests

requests.post("http://127.0.0.1:3001/auth/register",data={"username":"James","password":"123456","email":"example@com"})
