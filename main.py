# main.py
from fastapi import FastAPI
from extractor import search_sql_in_repo, save_to_excel, sql_patterns
from typing import Optional
import os
import uuid
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
import shutil
from extractor import extract_zip, decompile_class_file
app = FastAPI()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_and_extract(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Handle zip/jar/class/java
        process_folder = f"{UPLOAD_DIR}/{file_id}_extracted"
        os.makedirs(process_folder, exist_ok=True)

        if file_path.endswith(".zip") or file_path.endswith(".jar"):
            extract_zip(file_path, process_folder)
        elif file_path.endswith(".class"):
            decompile_class_file(file_path, process_folder)
        elif file_path.endswith(".java") or file_path.endswith(".sql"):
            shutil.copy(file_path, process_folder)
        else:
            return {"message": "Unsupported file type."}

        # Scan for SQL
        queries = search_sql_in_repo(process_folder, sql_patterns)
        # Save to Excel
        excel_file_path = f"{UPLOAD_DIR}/SQL_Report_{file_id}.xlsx"
        save_to_excel(queries, excel_file_path)

        return {
            "message": f"Processed {file.filename}",
            "query_count": len(queries),
            "excel_download_url": f"/download/{os.path.basename(excel_file_path)}"
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/download/{filename}")
async def download_excel(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)
    return {"error": "File not found"}
@app.get("/")
def read_root():
    return {"message": "SQL Extractor API is running"}

@app.post("/extract-sql/")
def extract_sql(repo_path: str = "samples", output_file: str = "sql_queries.xlsx"):
    try:
        results = search_sql_in_repo(repo_path, sql_patterns)
        if results:
            save_to_excel(results, output_file)
            return {"message": f"Extraction completed. {len(results)} queries found.", "output_file": output_file}
        return {"message": "No SQL queries found."}
    except Exception as e:
        return {"error": str(e)}
