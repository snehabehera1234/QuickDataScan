from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io

app = FastAPI(title="Data Quality Checker API")


@app.post("/check/")
async def check_data(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    result = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "data_types": df.dtypes.astype(str).to_dict()
    }
    return result

