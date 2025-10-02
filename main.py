import os
import base64
from io import BytesIO
from typing import Dict, List
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Table Processing API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class TableData(BaseModel):
    headers: List[str]
    rows: List[List[str]]

# Configuration
OPENAI_API_KEY = os.getenv("API_KEY_OPEN_AI")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def encode_image_to_base64(image_bytes: bytes) -> str:
    """
    Encode image bytes to base64 string.
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def validate_image(image_bytes: bytes) -> bool:
    """
    Validate that the uploaded file is a valid image.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        img.verify()
        return True
    except Exception:
        return False

async def process_image_with_vision_api(image_base64: str) -> Dict[str, List]:
    """
    Send image to OpenAI's GPT-4 Vision API to extract table data.
    Returns structured table data with headers and rows.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API_KEY_OPEN_AI environment variable not set. Please add it to your .env file."
        )
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this image and extract any table data you find. 
                        Return ONLY a valid JSON object with this exact structure:
                        {
                            "headers": ["Column1", "Column2", ...],
                            "rows": [
                                ["cell1", "cell2", ...],
                                ["cell1", "cell2", ...],
                                ...
                            ]
                        }
                        
                        Rules:
                        - Extract all visible table data accurately
                        - Preserve the exact text content from each cell
                        - Headers should be the first row or column labels
                        - Each row must have the same number of cells as there are headers
                        - Return ONLY the JSON, no other text or markdown
                        - If no table is found, return empty arrays for headers and rows
                        """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.1
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENAI_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Unknown error"
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API error: {error_detail}"
            )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse the JSON response
        import json
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            table_data = json.loads(content)
            return table_data
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse AI response as JSON: {str(e)}\nResponse: {content}"
            )

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the main table processing interface.
    """
    return templates.TemplateResponse("table.html", {"request": request})

@app.get("/whack-a-mole", response_class=HTMLResponse)
async def whack_a_mole(request: Request):
    """
    Serve the whack-a-table game with a 4x4 table.
    """
    return templates.TemplateResponse("whack_a_mole.html", {"request": request})

@app.get("/joke", response_class=HTMLResponse)
async def joke_page(request: Request):
    """
    Serve the joke/splash page with the table drawer.
    """
    return templates.TemplateResponse("joke.html", {"request": request})

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "message": "Table Processing API is running"}

@app.post("/api/process_table", response_model=TableData)
async def process_table(file: UploadFile = File(...)):
    """
    Process a table screenshot and extract structured data.
    
    This endpoint:
    1. Accepts an image file (screenshot of a table)
    2. Validates it's a valid image
    3. Sends it to OpenAI's GPT-4 Vision API
    4. Extracts table data (headers and rows)
    5. Returns structured JSON for rendering
    
    Returns:
        TableData: Object containing headers and rows arrays
    """
    # Read uploaded file
    image_bytes = await file.read()
    
    # Validate image
    is_valid = validate_image(image_bytes)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. Please upload a valid image (JPEG, PNG, etc.)"
        )
    
    # Convert to base64
    image_base64 = encode_image_to_base64(image_bytes)
    
    # Process with Vision API
    try:
        table_data = await process_image_with_vision_api(image_base64)
        
        # Validate response structure
        if "headers" not in table_data or "rows" not in table_data:
            raise HTTPException(
                status_code=500,
                detail="Invalid response structure from AI model"
            )
        
        return TableData(**table_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
