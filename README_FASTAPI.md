# Table Screenshot Processor

A modern web application that uses AI vision to extract table data from screenshots and convert them into editable, Notion-style tables.

## Features

- 🖼️ **Upload Screenshots**: Drag-and-drop or click to upload table screenshots
- 🤖 **AI-Powered Extraction**: Uses OpenAI's GPT-4 Vision API to accurately extract table data
- ✏️ **Notion-Style Editing**: Edit any cell directly in the browser with Notion's familiar UX
- 📊 **CSV Export**: Export your edited tables to CSV format
- 🎨 **Modern UI**: Beautiful, responsive interface built with Tailwind CSS

## Prerequisites

- Python 3.8+
- OpenAI API key (for GPT-4 Vision access)

## Installation

1. **Clone the repository** (or navigate to the project directory):
```bash
cd /home/julesc/Delos/hackathon-table
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the project root:
```bash
echo "API_KEY_OPEN_AI=your-openai-api-key-here" > .env
```

Or export the variable:
```bash
export API_KEY_OPEN_AI="your-openai-api-key-here"
```

## Usage

### Running the FastAPI Application

Start the server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Using the Application

1. **Open the web interface** at http://localhost:8000
2. **Upload a screenshot** of a table by:
   - Clicking the upload area
   - Dragging and dropping an image file
3. **Click "Process Table"** to extract the data
4. **Edit the table** by clicking on any cell
5. **Export to CSV** using the export button

## API Endpoints

### POST `/api/process_table`

Process a table screenshot and extract structured data.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload (image)

**Response:**
```json
{
  "headers": ["Column 1", "Column 2", "Column 3"],
  "rows": [
    ["Row 1 Cell 1", "Row 1 Cell 2", "Row 1 Cell 3"],
    ["Row 2 Cell 1", "Row 2 Cell 2", "Row 2 Cell 3"]
  ]
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/process_table" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@table_screenshot.png"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/api/process_table"
files = {"file": open("table_screenshot.png", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Architecture

### Backend (FastAPI)

- **Framework**: FastAPI for high-performance async API
- **Image Processing**: Pillow for image validation
- **AI Vision**: OpenAI GPT-4o for table extraction
- **Validation**: Pydantic models for type safety

### Frontend

- **Styling**: Tailwind CSS + custom Notion-inspired styles
- **Interaction**: Vanilla JavaScript for lightweight performance
- **Features**:
  - Drag-and-drop file upload
  - Image preview
  - Real-time cell editing
  - CSV export functionality

## Project Structure

```
hackathon-table/
├── main.py                 # FastAPI application
├── app.py                  # Original Flask app (legacy)
├── requirements.txt        # Python dependencies
├── static/                 # Static assets
│   ├── table.jpg
│   └── drawer.jpg
├── templates/              # HTML templates
│   ├── table.html         # Main FastAPI interface
│   ├── index.html         # Flask interface
│   └── joke.html          # Splash page
└── README_FASTAPI.md      # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY_OPEN_AI` | Your OpenAI API key for GPT-4 Vision | Yes |

## Error Handling

The application includes comprehensive error handling:

- **Invalid Image**: Returns 400 error if uploaded file is not a valid image
- **API Errors**: Returns appropriate error codes with descriptive messages
- **No Table Found**: Gracefully handles images without tables
- **Network Issues**: Displays user-friendly error messages in the UI

## Performance Considerations

- **Async Processing**: Uses async/await for non-blocking I/O
- **Timeouts**: 60-second timeout for API calls
- **Image Validation**: Pre-validates images before sending to API
- **Base64 Encoding**: Efficient image encoding for API transmission

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn main:app --reload

# With custom port
uvicorn main:app --reload --port 8080

# With debug logging
uvicorn main:app --reload --log-level debug
```

### API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### "API_KEY_OPEN_AI environment variable not set"
Make sure you've created a `.env` file with your API key:
```bash
echo "API_KEY_OPEN_AI=your-key-here" > .env
```

Or export it:
```bash
export API_KEY_OPEN_AI="your-key-here"
```

### CORS Errors
The app allows all origins by default. If you need to restrict:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Restrict origins
    ...
)
```

### Port Already in Use
Change the port in the command:
```bash
uvicorn main:app --port 8001
```

## License

This project is part of a hackathon and is provided as-is for educational purposes.

## Credits

- **UI Inspiration**: Notion's table interface
- **AI Model**: OpenAI GPT-4o Vision
- **Framework**: FastAPI by Sebastián Ramírez 