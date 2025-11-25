from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from llm.client import LLMClient
from core.parser import parse_clauses_from_llm
from core.resolver import prove_statement

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class SolveRequest(BaseModel):
    task: str


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')


@app.post("/api/solve")
async def solve_logic(req: SolveRequest):
    client = LLMClient()

    llm_json = client.formalize(req.task)
    if "Error" in llm_json:
        raise HTTPException(status_code=500, detail=llm_json)

    clauses = parse_clauses_from_llm(llm_json)

    is_proved, logs = prove_statement(clauses)

    explanation = client.explain(req.task, logs)

    return {
        "formalization": llm_json,
        "logs": logs,
        "explanation": explanation,
        "status": is_proved
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)