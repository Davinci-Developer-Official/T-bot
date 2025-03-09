from fastapi import FastAPI
import MetaTrader5 as mt5

app = FastAPI()

@app.get("/")
def read_first():
    print("hello fast api is running")
    return {"message":"Hello,Fast Api is running"}

@app.get("/mt5")
def init():
    # open = mt5.initialize()
    return "mt5 opening ........"