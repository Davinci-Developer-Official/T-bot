from fastapi import FastAPI

app = FastAPI()

@app.get("/first")
def read_first():
    print("hello fast api is running")
    return {"message":"Hello,Fast Api is running"}
