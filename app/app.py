from fastapi import FastAPI, HTTPException
import duckdb
import pyreadstat
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement de la base de données
sav_file = "Employee.sav"
df, meta = pyreadstat.read_sav(sav_file)

# Connexion à DuckDB
conn = duckdb.connect('data.db')
conn.register("data", df)

class QueryModel(BaseModel):
    sql: str
    limit: Optional[int] = 100

@app.get("/")
def read_root():
    return {"message": "API pour interroger les données employés"}

@app.post("/query/")
def execute_query(query: QueryModel):
    try:
        sql = query.sql
        if "LIMIT" not in sql.upper() and query.limit is not None:
            sql += f" LIMIT {query.limit}"
            
        result = conn.execute(sql).fetchdf()
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    
    