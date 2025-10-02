import os
import io
import asyncio
import tempfile
from typing import Optional
import edge_tts
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
import threading
import queue

class TextToSpeechEngine:
    """Real-time text-to-speech engine with multiple backends"""
    
    def __init__(self):
        self.edge_voices = []
        self.current_voice = "en-US-AriaNeural"
        self.rate = 1.0
        self.volume = 1.0
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.playback_thread = None
        
        # Initialize pyttsx3 engine for offline TTS
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty('rate', 150)  # Speed of speech
            self.offline_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        except Exception as e:
            print(f"Warning: Could not initialize offline TTS engine: {e}")
            self.offline_engine = None
    
    async def get_available_voices(self) -> list:
        """Get list of available voices from Edge TTS"""
        try:
            voices = await edge_tts.list_voices()
            self.edge_voices = [voice for voice in voices if voice['Locale'].startswith('en')]
            return self.edge_voices
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []
    
    async def synthesize_edge_tts(self, text: str, voice: Optional[str] = None) -> bytes:
        """
        Synthesize speech using Edge TTS (online, high quality)
        
        Args:
            text: Text to synthesize
            voice: Voice to use (defaults to current voice)
            
        Returns:
            Audio data as bytes
        """
        if voice is None:
            voice = self.current_voice
        
        try:
            communicate = edge_tts.Communicate(text, voice, rate=f"+{int((self.rate - 1) * 100)}%")
            audio_data = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return b""
    
    def synthesize_offline_tts(self, text: str) -> bytes:
        """
        Synthesize speech using pyttsx3 (offline, basic quality)
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        if not self.offline_engine:
            return b""
        
        try:
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Save speech to file
            self.offline_engine.save_to_file(text, temp_path)
            self.offline_engine.runAndWait()
            
            # Read the generated audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return audio_data
        except Exception as e:
            print(f"Offline TTS error: {e}")
            return b""
    
    async def speak_async(self, text: str, use_edge: bool = True, voice: Optional[str] = None) -> bytes:
        """
        Asynchronously synthesize speech
        
        Args:
            text: Text to speak
            use_edge: Use Edge TTS if True, offline TTS if False
            voice: Voice to use (only for Edge TTS)
            
        Returns:
            Audio data as bytes
        """
        if use_edge:
            return await self.synthesize_edge_tts(text, voice)
        else:
            # Run offline TTS in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.synthesize_offline_tts, text)
    
    def speak_sync(self, text: str, use_edge: bool = True, voice: Optional[str] = None):
        """
        Synchronously synthesize and play speech
        
        Args:
            text: Text to speak
            use_edge: Use Edge TTS if True, offline TTS if False
            voice: Voice to use (only for Edge TTS)
        """
        if use_edge:
            # Run Edge TTS in thread
            def run_edge_tts():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_data = loop.run_until_complete(self.synthesize_edge_tts(text, voice))
                loop.close()
                if audio_data:
                    self._play_audio_data(audio_data)
            
            thread = threading.Thread(target=run_edge_tts)
            thread.start()
        else:
            audio_data = self.synthesize_offline_tts(text)
            if audio_data:
                self._play_audio_data(audio_data)
    
    def _play_audio_data(self, audio_data: bytes):
        """Play audio data from bytes"""
        try:
            # Convert bytes to AudioSegment
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            
            # Adjust volume
            if self.volume != 1.0:
                audio = audio + (20 * (self.volume - 1.0))  # Volume adjustment in dB
            
            # Play audio
            play(audio)
        except Exception as e:
            print(f"Error playing audio: {e}")
            # Fallback: just print the text instead of playing audio
            print("Audio playback not available, but text-to-speech generation succeeded.")
    
    def set_voice(self, voice: str):
        """Set the voice for Edge TTS"""
        self.current_voice = voice
    
    def set_rate(self, rate: float):
        """Set speech rate (0.5 to 2.0)"""
        self.rate = max(0.5, min(2.0, rate))
        if self.offline_engine:
            self.offline_engine.setProperty('rate', int(150 * rate))
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.offline_engine:
            self.offline_engine.setProperty('volume', volume)
    
    def stop_speaking(self):
        """Stop current speech"""
        # This is a basic implementation - pyttsx3 doesn't have easy stop functionality
        # For production, you might want to use a more advanced TTS library
        pass

class VoiceFeedback:
    """Voice feedback system for table operations"""
    
    def __init__(self):
        self.tts = TextToSpeechEngine()
        self.enabled = True
    
    def speak_table_created(self, headers: list, row_count: int):
        """Provide voice feedback when table is created"""
        if not self.enabled:
            return
        
        text = f"Table created successfully with {len(headers)} columns and {row_count} rows. Columns are: {', '.join(headers)}"
        self.tts.speak_sync(text)
    
    def speak_table_edited(self, changes: str):
        """Provide voice feedback when table is edited"""
        if not self.enabled:
            return
        
        text = f"Table updated. {changes}"
        self.tts.speak_sync(text)
    
    def speak_error(self, error_message: str):
        """Provide voice feedback for errors"""
        if not self.enabled:
            return
        
        text = f"Error: {error_message}"
        self.tts.speak_sync(text)
    
    def speak_voice_processed(self, transcription: str):
        """Provide voice feedback when voice input is processed"""
        if not self.enabled:
            return
        
        text = f"I heard: {transcription}. Processing your request now."
        self.tts.speak_sync(text)
    
    def speak_processing(self, operation: str):
        """Provide voice feedback during processing"""
        if not self.enabled:
            return
        
        text = f"Processing {operation}. Please wait."
        self.tts.speak_sync(text)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable voice feedback"""
        self.enabled = enabled

# Global instances
tts_engine = TextToSpeechEngine()
voice_feedback = VoiceFeedback()

# Utility functions
async def text_to_speech(text: str, voice: Optional[str] = None, use_edge: bool = True) -> bytes:
    """Convert text to speech and return audio bytes"""
    return await tts_engine.speak_async(text, use_edge, voice)

def speak_text(text: str, voice: Optional[str] = None, use_edge: bool = True):
    """Convert text to speech and play immediately"""
    tts_engine.speak_sync(text, use_edge, voice)

def get_available_voices() -> list:
    """Get list of available voices"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    voices = loop.run_until_complete(tts_engine.get_available_voices())
    loop.close()
    return voices
