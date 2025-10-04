# OverwatchAgent - AI-Powered Coding Assistant

An intelligent coding agent that can understand high-level software development requests, break them down into structured plans, and execute them step-by-step with human oversight.

## 🚀 Features

- **Voice Input**: Speak your project goals naturally using voice commands
- **Intelligent Planning**: AI-powered project breakdown into manageable tasks
- **Human Approval**: Review and approve generated plans before execution
- **Step-by-Step Execution**: Execute tasks with pause between each completion
- **Real-time Feedback**: See agent thoughts, tool calls, and results in real-time
- **Dependency Management**: Automatic task dependency resolution
- **Progress Tracking**: Monitor completion status and upcoming tasks

## 📋 Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)

### Required API Access
- **Google API Key**: For AI model access
- **Google Cloud Project** (optional): For advanced features

## 🛠️ Installation

### 1. Clone or Download the Project
```bash
# If you have the project files, navigate to the directory
cd /path/to/coding_agent
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install google-adk pydantic

# Install voice input dependencies
pip install SpeechRecognition PyAudio
```

### 4. System Dependencies for Voice Input

#### macOS
```bash
brew install portaudio
```

#### Ubuntu/Debian
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
```

#### Windows
Usually works with pip install, but if you encounter issues:
- Download and install Microsoft Visual C++ Build Tools
- Install PyAudio from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

## 🔑 Environment Setup

### 1. Set Google API Key
You need a valid Google API key to use the AI models. Get one from the [Google AI Studio](https://aistudio.google.com/app/apikey).

#### Option A: Environment Variable (Recommended)
```bash
# Set for current session
export GOOGLE_API_KEY="your-api-key-here"

# Set permanently (add to ~/.bashrc, ~/.zshrc, or ~/.profile)
echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Option B: Create .env File
```bash
# Create .env file in the project root
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

#### Option C: Set in Terminal Before Running
```bash
# Run with environment variable
GOOGLE_API_KEY="your-api-key-here" python3 run.py
```

### 2. Verify API Key
```bash
# Test that the API key is set
echo $GOOGLE_API_KEY
```

## 🎯 Usage

### Quick Start
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the application
python3 run.py
```

### Step-by-Step Workflow

1. **Start the Application**
   ```bash
   python3 run.py
   ```

2. **Provide Project Goal**
   - Speak your request clearly into the microphone
   - Example: "Create a Flask web application with user authentication"
   - If voice input fails, you'll be prompted to type your request

3. **Review Generated Plan**
   - The AI will analyze your request and create a structured plan
   - Review the plan details including:
     - Project description
     - Technology stack
     - Task breakdown
     - Estimated timeline
   - Approve by typing `y` or reject with `n`

4. **Execute Tasks**
   - Tasks will execute one by one in dependency order
   - After each task completion, you'll see:
     - Task summary
     - Final output from the AI
     - Progress status
     - Next upcoming tasks
   - Press `Enter` to continue to the next task

5. **Monitor Progress**
   - Watch real-time agent thoughts and tool calls
   - Review generated files in the `generated_project/` directory
   - Track overall progress and remaining tasks

## 📁 Project Structure

```
coding_agent/
├── run.py                    # Main entry point
├── src/
│   ├── overwatch_agent.py   # Core OverwatchAgent class
│   ├── agents/
│   │   ├── planner_agent.py # AI agent for project planning
│   │   └── executor_agent.py # AI agent for task execution
│   └── tools/
│       ├── file_system_tools.py # File operations
│       └── voice_input.py   # Voice input handling
├── generated_project/       # Output directory for created projects
├── venv/                   # Virtual environment
└── README.md              # This file
```

## 🔧 Configuration

### Customize Agent Behavior
Edit `src/overwatch_agent.py` to modify:
- Default app name and user ID
- Voice input preferences
- Session management settings

### Modify Agent Instructions
Edit `src/agents/planner_agent.py` and `src/agents/executor_agent.py` to customize:
- AI agent personas and instructions
- Output schemas and formatting
- Tool configurations

## 🐛 Troubleshooting

### Common Issues

#### 1. "API key not valid" Error
```bash
# Verify API key is set correctly
echo $GOOGLE_API_KEY

# Re-export with correct key
export GOOGLE_API_KEY="your-correct-api-key"
```

#### 2. Voice Input Dependencies Missing
```bash
# Reinstall voice dependencies
pip uninstall SpeechRecognition PyAudio
pip install SpeechRecognition PyAudio

# On macOS, ensure portaudio is installed
brew install portaudio
```

#### 3. "Module not found" Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall all dependencies
pip install -r requirements.txt
```

#### 4. Permission Errors on macOS
```bash
# Grant microphone permissions to Terminal/iTerm
# System Preferences > Security & Privacy > Privacy > Microphone
```

### Getting Help

1. **Check Dependencies**: Ensure all required packages are installed
2. **Verify API Key**: Confirm Google API key is valid and properly set
3. **Check Permissions**: Ensure microphone access is granted
4. **Review Logs**: Check console output for detailed error messages

## 📝 Example Usage

### Example 1: Web Application
```
User: "Create a Flask web application with a home page and contact form"
→ AI generates plan with tasks for Flask setup, templates, routes
→ User approves plan
→ Tasks execute: create app.py, templates/, static files
→ User presses Enter between each task
→ Final result: Complete Flask application in generated_project/
```

### Example 2: Data Analysis Script
```
User: "Build a Python script to analyze CSV data and create visualizations"
→ AI creates plan with pandas, matplotlib tasks
→ User reviews and approves
→ Tasks execute: data loading, analysis, plotting
→ User controls pace with Enter key
→ Result: Analysis script with generated charts
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Agent Development Kit (ADK) for AI agent framework
- Google AI models for natural language processing
- Python community for excellent libraries and tools

---

**Ready to start coding with AI? Run `python3 run.py` and speak your first project goal!** 🚀
