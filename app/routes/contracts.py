from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import uuid
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
from service.doc_parser import extract_text
from models import Contract
from database import contracts_collection

router = APIRouter(prefix="/contracts",tags=["contracts"])

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT contract for analysis.
    """
    # Implementation for uploading a contract goes here
    ext=os.path.splitext(file.filename)[1].lower()       #Check the file extension
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail={"error": "Invalid file type. Only PDF and TXT files are allowed."})

    content = await file.read()

    size_mb=len(content) / (1024 * 1024)  # Convert bytes to MB

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail={"error": f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB} MB."})

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name=f"{uuid.uuid4().hex}{ext}"
    file_path=os.path.join(UPLOAD_DIR, unique_name)

    with open (file_path, "wb") as f:
        f.write(content)

    parsed_text=extract_text(file_path)

    contract_data=Contract(
        filename=unique_name,
        original_name=file.filename,
        text_content=parsed_text["text"] if isinstance(parsed_text, dict) else parsed_text,
        page_count=int(parsed_text["page_count"]) if isinstance(parsed_text, dict) else len(parsed_text.splitlines()),
        word_count=int(parsed_text["word_count"]) if isinstance(parsed_text, dict) else len(parsed_text.split()),
    )

    doc=contract_data.model_dump()
    result=contracts_collection.insert_one(doc)
    contract_data.id=str(result.inserted_id)

    return {
        "message": "Contract uploaded successfully", 
        "contract": contract_data.model_dump(),
        "id": contract_data.id
        }

@router.get("/")
async def list_contracts():
    """
    List all uploaded contracts
    """
    contracts=[]
    for doc in contracts_collection.find({}, {"text_content":0}):
        contract= Contract(**doc)
        contract.id=str(doc["_id"])
        contracts.append(contract.model_dump())
    return {"contracts": contracts}


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """
    Retrieve a specific contract by its ID.
    """
    from bson import ObjectId
    doc=contracts_collection.find_one({"_id": ObjectId(contract_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract=Contract(**doc)
    contract.id=str(doc["_id"])

    return {"contract": contract.model_dump()}

