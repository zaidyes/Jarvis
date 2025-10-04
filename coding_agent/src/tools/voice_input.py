"""
Voice input tools for capturing audio from microphone and transcribing to text.

This module provides functionality to capture audio input from the user's microphone
and convert it to text using speech recognition. Includes automatic dependency
management and robust error handling for various audio input scenarios.
"""

import sys
import subprocess
import importlib.util


def _check_and_install_dependencies():
    """
    Check if required dependencies are installed and provide installation instructions.
    
    This function checks for SpeechRecognition and PyAudio libraries and provides
    clear instructions for installation if they are missing.
    """
    required_packages = {
        'speech_recognition': 'SpeechRecognition',
        'pyaudio': 'PyAudio'
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required dependencies for voice input:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 To install the missing packages, run:")
        print("   pip install SpeechRecognition PyAudio")
        print("\n⚠️  Note: On some systems, you may need to install additional dependencies:")
        print("   - macOS: brew install portaudio")
        print("   - Ubuntu/Debian: sudo apt-get install python3-pyaudio portaudio19-dev")
        print("   - Windows: Usually works with pip install")
        print("\n🔄 Please install the dependencies and try again.")
        return False
    
    return True


def get_voice_command() -> str:
    """
    Capture audio from the user's microphone and transcribe it to text.
    
    This function uses the speech_recognition library to listen for audio input
    from the default microphone, transcribes it to text, and returns the result.
    Includes comprehensive error handling for various scenarios.
    
    Returns:
        str: The transcribed text from the audio input.
        
    Raises:
        ImportError: If required dependencies are not installed.
        RuntimeError: If microphone is not available or audio cannot be captured.
        ValueError: If audio is not understood or transcription fails.
    """
    # Check dependencies first
    if not _check_and_install_dependencies():
        raise ImportError("Required dependencies for voice input are not installed.")
    
    try:
        import speech_recognition as sr
    except ImportError:
        raise ImportError("SpeechRecognition library is not installed. Run: pip install SpeechRecognition")
    
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    try:
        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            print("🎤 Adjusting for ambient noise...")
            # Adjust for ambient noise for better recognition
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("👂 Listening... Speak now!")
            # Listen for audio input with a timeout
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
        print("🔄 Processing audio...")
        
        try:
            # Use Google's speech recognition service
            text = recognizer.recognize_google(audio)
            print(f"✅ Transcribed: '{text}'")
            return text
            
        except sr.UnknownValueError:
            error_msg = "❌ Could not understand the audio. Please try speaking more clearly."
            print(error_msg)
            raise ValueError(error_msg)
            
        except sr.RequestError as e:
            error_msg = f"❌ Speech recognition service error: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
            
    except sr.WaitTimeoutError:
        error_msg = "❌ No audio detected within the timeout period. Please try again."
        print(error_msg)
        raise RuntimeError(error_msg)
        
    except OSError as e:
        if "No such file or directory" in str(e) or "device not found" in str(e).lower():
            error_msg = "❌ Microphone not found or not accessible. Please check your microphone connection."
            print(error_msg)
            raise RuntimeError(error_msg)
        else:
            error_msg = f"❌ Audio system error: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
            
    except Exception as e:
        error_msg = f"❌ Unexpected error during voice input: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)


def test_microphone_availability() -> bool:
    """
    Test if microphone is available and accessible.
    
    Returns:
        bool: True if microphone is available, False otherwise.
    """
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("✅ Microphone is available and accessible.")
            return True
            
    except ImportError:
        print("❌ SpeechRecognition library not installed.")
        return False
    except OSError as e:
        if "No such file or directory" in str(e) or "device not found" in str(e).lower():
            print("❌ Microphone not found or not accessible.")
            return False
        else:
            print(f"❌ Audio system error: {str(e)}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error testing microphone: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the microphone availability
    print("🔍 Testing microphone availability...")
    if test_microphone_availability():
        print("\n🎯 Testing voice command capture...")
        try:
            result = get_voice_command()
            print(f"\n🎉 Success! Captured voice command: '{result}'")
        except Exception as e:
            print(f"\n💥 Error during voice capture: {str(e)}")
    else:
        print("\n❌ Cannot proceed with voice testing due to microphone issues.")
