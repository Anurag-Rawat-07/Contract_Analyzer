from fastapi import FastAPI
from routes import contracts
from routes.analysis import router as analysis_router
from database import init_db 

app=FastAPI(
    title="Contact API",
    description="AI-Powered Contact Analysis using Gemini",
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {
        "app": "Contact Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "POST /contracts/upload": "Upload a PDF or TXT contact for analysis",
            "GET /contracts/": "Retrieve a list of all uploaded contracts",
            "GET /contracts/{contract_id}": "Retrieve details of a specific contract by ID",
            "POST/analysis/analyze/{contract_id}": "Analyze a specific contract by ID and return insights",
            "GET /analysis/{analysis_id}": "Retrieve analysis insights for a specific contract by ID",
            "GET /analysis/contract/{contract_id}": "Retrieve a list of all analyses for a specific contract by ID"
        }
    }

app.include_router(contracts.router)
app.include_router(analysis_router)

