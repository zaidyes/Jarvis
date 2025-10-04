#!/usr/bin/env python3
"""
Test script for voice input functionality.

This script tests the get_voice_command() function from voice_input.py.
It will attempt to capture audio from the microphone and transcribe it to text.
Requires human interaction to speak into the microphone.

Usage:
    python test_voice.py

Note: This test requires:
1. A working microphone
2. Internet connection (for Google Speech Recognition API)
3. SpeechRecognition and PyAudio libraries installed
"""

import sys
import os

# Add the src directory to the Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tools.voice_input import get_voice_command, test_microphone_availability
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the coding_agent directory.")
    sys.exit(1)


def main():
    """Main test function for voice input."""
    print("🎤 Voice Input Test")
    print("=" * 50)
    
    # Test microphone availability first
    print("\n1️⃣ Testing microphone availability...")
    if not test_microphone_availability():
        print("\n❌ Test failed: Microphone is not available.")
        print("Please check your microphone connection and try again.")
        return False
    
    # Test voice command capture
    print("\n2️⃣ Testing voice command capture...")
    print("📝 Instructions:")
    print("   - You will have 10 seconds to start speaking")
    print("   - Speak clearly for up to 5 seconds")
    print("   - The system will transcribe your speech to text")
    print("   - Press Ctrl+C to cancel if needed")
    
    try:
        print("\n🎯 Ready to capture voice input...")
        result = get_voice_command()
        
        print(f"\n✅ SUCCESS!")
        print(f"📝 Transcribed text: '{result}'")
        print(f"📊 Text length: {len(result)} characters")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️  Test cancelled by user.")
        return False
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("   - Make sure your microphone is working")
        print("   - Check your internet connection")
        print("   - Try speaking more clearly")
        print("   - Ensure SpeechRecognition and PyAudio are installed")
        return False


if __name__ == "__main__":
    print("🚀 Starting voice input test...")
    print("⚠️  This test requires human interaction - please be ready to speak!")
    
    try:
        success = main()
        
        if success:
            print("\n🎉 Voice input test completed successfully!")
            print("✅ The get_voice_command() function is working correctly.")
        else:
            print("\n💥 Voice input test failed.")
            print("❌ Please check the error messages above and try again.")
            
    except Exception as e:
        print(f"\n💥 Unexpected error during test: {str(e)}")
        print("❌ Test failed due to unexpected error.")
    
    print("\n👋 Test completed. Thank you for testing!")
