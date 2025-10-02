import os
import json
import tempfile
from typing import Dict, List, Optional
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class VoiceTableRequest(BaseModel):
    """Model for voice-based table creation requests"""
    description: str
    headers: Optional[List[str]] = None
    rows: Optional[List[List[str]]] = None

class VoiceEditRequest(BaseModel):
    """Model for voice-based table editing requests"""
    table_data: Dict
    edit_instruction: str

class VoiceProcessor:
    """Handles voice processing using OpenAI's Whisper API"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("API_KEY_OPEN_AI")
        self.whisper_url = "https://api.openai.com/v1/audio/transcriptions"
        self.chat_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.openai_api_key:
            raise ValueError("API_KEY_OPEN_AI environment variable not set")
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using OpenAI's Whisper API
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        files = {
            "file": open(audio_file_path, "rb"),
            "model": (None, "whisper-1"),
            "language": (None, "en"),  # Optional: specify language
            "response_format": (None, "text")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.whisper_url,
                headers=headers,
                files=files
            )
            
            if response.status_code != 200:
                error_detail = response.text if response.text else "Unknown error"
                raise Exception(f"Whisper API error: {error_detail}")
            
            return response.text.strip()
    
    async def create_table_from_voice_description(self, description: str) -> Dict[str, List]:
        """
        Generate table structure from voice description using GPT-4
        
        Args:
            description: Voice-transcribed description of the table
            
        Returns:
            Dictionary with headers and rows
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        prompt = f"""
        Based on this voice description: "{description}"
        
        Create a table structure. Return ONLY a valid JSON object with this exact structure:
        {{
            "headers": ["Column1", "Column2", ...],
            "rows": [
                ["cell1", "cell2", ...],
                ["cell1", "cell2", ...],
                ...
            ]
        }}
        
        Rules:
        - Generate appropriate column headers based on the description
        - Create 3-5 sample rows with realistic data
        - Make sure the table makes sense for the described purpose
        - ALL values must be strings (wrap numbers in quotes)
        - Return ONLY the JSON, no other text or markdown
        - If the description is unclear, make reasonable assumptions
        - Example: "rows": [["John", "25", "Engineer"], ["Jane", "30", "Manager"]]
        """
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.chat_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_detail = response.json() if response.text else "Unknown error"
                raise Exception(f"OpenAI API error: {error_detail}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                table_data = json.loads(content)
                
                # Ensure all data is converted to strings
                if "headers" in table_data:
                    table_data["headers"] = [str(header) for header in table_data["headers"]]
                if "rows" in table_data:
                    table_data["rows"] = [[str(cell) for cell in row] for row in table_data["rows"]]
                
                return table_data
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {content}")
    
    async def edit_table_from_voice_instruction(self, table_data: Dict, edit_instruction: str) -> Dict[str, List]:
        """
        Edit existing table based on voice instruction using GPT-4
        
        Args:
            table_data: Current table data (headers and rows)
            edit_instruction: Voice-transcribed editing instruction
            
        Returns:
            Updated table data
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        current_table = json.dumps(table_data, indent=2)
        
        prompt = f"""
        Current table data:
        {current_table}
        
        Voice instruction: "{edit_instruction}"
        
        Apply the instruction to modify the table. Return ONLY a valid JSON object with this exact structure:
        {{
            "headers": ["Column1", "Column2", ...],
            "rows": [
                ["cell1", "cell2", ...],
                ["cell1", "cell2", ...],
                ...
            ]
        }}
        
        Rules:
        - Follow the voice instruction precisely
        - Maintain the same JSON structure
        - If adding columns, update all existing rows with appropriate values
        - If removing columns, remove them from all rows
        - If modifying data, make the changes as requested
        - ALL values must be strings (wrap numbers in quotes)
        - Return ONLY the JSON, no other text or markdown
        - Example: "rows": [["John", "25", "Engineer"], ["Jane", "30", "Manager"]]
        """
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.chat_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_detail = response.json() if response.text else "Unknown error"
                raise Exception(f"OpenAI API error: {error_detail}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                updated_table = json.loads(content)
                
                # Ensure all data is converted to strings
                if "headers" in updated_table:
                    updated_table["headers"] = [str(header) for header in updated_table["headers"]]
                if "rows" in updated_table:
                    updated_table["rows"] = [[str(cell) for cell in row] for row in updated_table["rows"]]
                
                return updated_table
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {content}")

# Global voice processor instance
voice_processor = VoiceProcessor()

# Example usage functions
async def process_voice_table_creation(audio_file_path: str) -> Dict[str, List]:
    """
    Process voice input to create a new table
    
    Args:
        audio_file_path: Path to the audio file containing table description
        
    Returns:
        Generated table data
    """
    # Transcribe audio to text
    description = await voice_processor.transcribe_audio(audio_file_path)
    
    # Generate table from description
    table_data = await voice_processor.create_table_from_voice_description(description)
    
    return table_data

async def process_voice_table_edit(audio_file_path: str, current_table: Dict) -> Dict[str, List]:
    """
    Process voice input to edit an existing table
    
    Args:
        audio_file_path: Path to the audio file containing edit instructions
        current_table: Current table data to be modified
        
    Returns:
        Updated table data
    """
    # Transcribe audio to text
    edit_instruction = await voice_processor.transcribe_audio(audio_file_path)
    
    # Apply edits to table
    updated_table = await voice_processor.edit_table_from_voice_instruction(current_table, edit_instruction)
    
    return updated_table

# Utility function to save audio file from bytes
def save_audio_file(audio_bytes: bytes, file_extension: str = "wav") -> str:
    """
    Save audio bytes to a temporary file
    
    Args:
        audio_bytes: Audio data as bytes
        file_extension: File extension (wav, mp3, etc.)
        
    Returns:
        Path to the saved temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}")
    temp_file.write(audio_bytes)
    temp_file.close()
    return temp_file.name

# Cleanup function
def cleanup_temp_file(file_path: str):
    """
    Clean up temporary file
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        os.unlink(file_path)
    except OSError:
        pass  # File might already be deleted
