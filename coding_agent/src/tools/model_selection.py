"""
Model selection utilities for Jarvis.

This module provides functionality to list available Google AI models
and allow users to select which model to use for their projects.
"""

import google.generativeai as genai
import os
from typing import List, Dict, Optional


def get_available_models() -> List[Dict[str, str]]:
    """
    Get a list of available Google AI models.
    
    Returns:
        List of dictionaries containing model information
    """
    try:
        # Set up the API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY environment variable not set")
            return []
        
        genai.configure(api_key=api_key)
        
        # List available models
        models = genai.list_models()
        
        available_models = []
        for model in models:
            # Filter for text generation models
            if 'generateContent' in model.supported_generation_methods:
                model_info = {
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': getattr(model, 'description', 'No description available'),
                    'version': getattr(model, 'version', 'Unknown'),
                    'input_token_limit': getattr(model, 'input_token_limit', 'Unknown'),
                    'output_token_limit': getattr(model, 'output_token_limit', 'Unknown')
                }
                available_models.append(model_info)
        
        return available_models
        
    except Exception as e:
        print(f"❌ Error fetching available models: {str(e)}")
        return []


def display_available_models(models: List[Dict[str, str]]) -> None:
    """
    Display available models in a formatted way.
    
    Args:
        models: List of model dictionaries
    """
    if not models:
        print("❌ No models available")
        return
    
    print("\n" + "="*80)
    print("🤖 AVAILABLE GOOGLE AI MODELS")
    print("="*80)
    
    for i, model in enumerate(models, 1):
        print(f"\n{i}. {model['display_name']}")
        print(f"   📝 Name: {model['name']}")
        print(f"   📄 Description: {model['description']}")
        print(f"   🔢 Version: {model['version']}")
        print(f"   📥 Input Tokens: {model['input_token_limit']}")
        print(f"   📤 Output Tokens: {model['output_token_limit']}")
        print("-" * 60)


def select_model_interactive(models: List[Dict[str, str]], current_model: str = None) -> Optional[str]:
    """
    Allow user to select a model interactively.
    
    Args:
        models: List of available models
        current_model: Currently selected model name
        
    Returns:
        Selected model name or None if cancelled
    """
    if not models:
        print("❌ No models available for selection")
        return None
    
    display_available_models(models)
    
    print(f"\n🎯 Current model: {current_model or 'Not set'}")
    print("\n📋 Model Selection Options:")
    print("  • Enter a number (1-{}) to select a model".format(len(models)))
    print("  • Enter 'current' to keep the current model")
    print("  • Enter 'cancel' to cancel selection")
    
    while True:
        try:
            choice = input("\n🤖 Select model (or 'current'/'cancel'): ").strip().lower()
            
            if choice == 'cancel':
                print("❌ Model selection cancelled")
                return None
            elif choice == 'current':
                print(f"✅ Keeping current model: {current_model}")
                return current_model
            elif choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(models):
                    selected_model = models[index]['name']
                    print(f"✅ Selected model: {models[index]['display_name']}")
                    print(f"📝 Model name: {selected_model}")
                    return selected_model
                else:
                    print(f"❌ Invalid selection. Please enter a number between 1 and {len(models)}")
            else:
                print("❌ Invalid input. Please enter a number, 'current', or 'cancel'")
                
        except KeyboardInterrupt:
            print("\n❌ Model selection cancelled")
            return None
        except Exception as e:
            print(f"❌ Error during model selection: {str(e)}")
            return None


def get_model_info(model_name: str) -> Optional[Dict[str, str]]:
    """
    Get detailed information about a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model information dictionary or None if not found
    """
    models = get_available_models()
    for model in models:
        if model['name'] == model_name:
            return model
    return None
