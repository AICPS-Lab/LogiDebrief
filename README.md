# LogiDebrief: Signal-Temporal Logic-Based Automated Debriefing

An automated debriefing system for emergency call analysis using Large Language Models and Signal-Temporal Logic. This research prototype demonstrates automated quality assurance for 911 emergency call handling.

📖 **Paper**: [LogiDebrief: A Signal-Temporal Logic based Automated Debriefing Approach with Large Language Models Integration](https://doi.org/10.24963/ijcai.2025/1065)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API account with API key
- OpenAI Assistants configured (see setup guide below)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AICPS-Lab/LogiDebrief.git
cd LogiDebrief
```

2. **Install dependencies**
```bash
# Minimal installation (recommended)
pip install -r requirements.txt

# Full installation (includes all development dependencies)
pip install -r requirements-full.txt
```

3. **Configure environment**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

4. **Set up OpenAI Assistants** (see detailed instructions below)

5. **Run with example data**
```bash
python main.py --example
```

## 📋 Configuration

### Environment Variables (.env file)
```bash
OPENAI_API_KEY=your_openai_api_key_here    # Required
LOG_LEVEL=INFO                              # Optional (DEBUG, INFO, WARNING, ERROR)
LOG_FILE=logidebrief.log                    # Optional log file path
```

### OpenAI Assistant Setup

You need to create 7 OpenAI Assistants and configure their IDs in `function_mappings.json`:

1. **Create Assistants** at [OpenAI Platform](https://platform.openai.com/assistants)
   - `address`: Validates address information
   - `phone`: Validates phone number collection
   - `name`: Validates caller name verification
   - `general`: General validation checks
   - `flags`: Identifies critical flags/protocols
   - `condition`: Evaluates preconditions
   - `check`: Validates specific protocol checks

2. **Configure Assistant IDs** in `function_mappings.json`:
```json
{
  "phone": "asst_xxxxxxxxxxxxx",
  "name": "asst_xxxxxxxxxxxxx",
  "address": "asst_xxxxxxxxxxxxx",
  "condition": "asst_xxxxxxxxxxxxx",
  "check": "asst_xxxxxxxxxxxxx",
  "flags": "asst_xxxxxxxxxxxxx",
  "general": "asst_xxxxxxxxxxxxx"
}
```

### Assistant Instructions Template

When creating each assistant, use instructions like:

**Address Assistant:**
```
You are an emergency call analyzer. Given a conversation transcript, evaluate if the dispatcher properly obtained and verified the address. Return a JSON with fields: ask-first, address-confirmation, obtained-address, double-checking-end, overall-eval, and explanations.
```

## 🎯 Usage

### Basic Usage
```bash
# Run with your own data
python main.py --conversation path/to/transcript.txt --task path/to/config.json

# Run with example data
python main.py --example

# Specify output location
python main.py --example --output results/analysis.json

# Validate configuration only
python main.py --validate-only
```

### Input File Formats

**Conversation File** (plain text):
```
Dispatcher: 911, what's your emergency?
Caller: I need help...
Dispatcher: What's your address?
...
```

**Task Configuration** (JSON):
```json
{
  "simulation_mode": "flash",
  "incident_spec": {
    "incident_type": "Abdominal or Back Pain",
    "address": "123 Main Street",
    "PD": false,
    "FD": false,
    "EMD": true
  }
}
```

## 📂 Project Structure

```
LogiDebrief/
├── main.py                 # Main application entry point
├── config.py              # Configuration management
├── functions/             # OpenAI integration module
│   └── __init__.py       # FunctionAgents class
├── guidecards/           # Emergency protocol guidelines
│   └── [incident_type]/  # Incident-specific protocols
│       ├── conditions.json
│       ├── questions.json
│       └── instructions.json
├── protocols/            # Critical life-saving protocols
│   └── [protocol_type]/ # Protocol-specific rules
├── examples/            # Sample data for testing
│   ├── sample_conversation.txt
│   └── sample_task.json
├── requirements.txt     # Core dependencies
├── requirements-full.txt # All dependencies
└── .env.example        # Environment configuration template
```

## 🔍 Features

- **Automated Call Analysis**: Evaluates emergency call handling against established protocols
- **Parallel Processing**: Optimized performance with concurrent validation
- **Comprehensive Checks**:
  - Address verification
  - Phone number collection
  - Caller identification
  - Medical questioning protocols
  - Pre-arrival instructions
  - Critical life-saving protocols
- **Flexible Configuration**: Support for multiple incident types and protocols
- **Detailed Logging**: Comprehensive logging for debugging and audit trails
- **Error Handling**: Robust error handling with retry logic for API calls

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ValueError: OPENAI_API_KEY not found
   ```
   Solution: Ensure your `.env` file contains a valid OpenAI API key

2. **Assistant ID Error**
   ```
   ValueError: Please configure the following assistant IDs
   ```
   Solution: Update `function_mappings.json` with valid Assistant IDs

3. **File Not Found**
   ```
   FileNotFoundError: Conversation file not found
   ```
   Solution: Check file paths and ensure files exist

4. **API Timeout**
   ```
   TimeoutError: Assistant run timed out
   ```
   Solution: Check internet connection and OpenAI API status

### Debug Mode

Enable detailed logging for troubleshooting:
```bash
# Set in .env file
LOG_LEVEL=DEBUG
```

## 📊 Output Format

The system generates a comprehensive JSON report including (see example snippet below):

```json
{
  "Call-taker obtained and verified the address": {
    "asked address first": true,
    "address double checking": true,
    "obtained address": true,
    "result": "YES",
    "explanation": "..."
  },
  "Call-taker used guidecards to obtain additional information?": {
    "result": "YES/NO/N/A",
    "explanation": "..."
  },
}
```

## 🔒 Security Notes

- **Never commit** your `.env` file or API keys
- Store sensitive configuration in environment variables
- Use `.gitignore` to exclude sensitive files
- Regularly rotate API keys
- Review [OpenAI's security best practices](https://help.openai.com/en/articles/5112595)

## 📚 API Documentation

For detailed API documentation and advanced usage, refer to:
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Assistants Guide](https://platform.openai.com/docs/assistants)

## 🤝 Contributing

This is a research prototype. The complete codebase with formalized guidecards and protocols will be released upon paper acceptance.

## 📄 Citation

If you use this code for research purposes, please cite our paper:

```bibtex
@inproceedings{ijcai2025p1065,
  title     = {LogiDebrief: A Signal-Temporal Logic Based Automated Debriefing Approach with Large Language Models Integration},
  author    = {Chen, Zirong and An, Ziyan and Reynolds, Jennifer and Mullen, Kristin and Maritini, Stephen and Ma, Meiyi},
  booktitle = {Proceedings of the Thirty-Fourth International Joint Conference on
               Artificial Intelligence, {IJCAI-25}},
  publisher = {International Joint Conferences on Artificial Intelligence Organization},
  editor    = {James Kwok},
  pages     = {9582--9590},
  year      = {2025},
  month     = {8},
  note      = {AI and Social Good},
  doi       = {10.24963/ijcai.2025/1065},
  url       = {https://doi.org/10.24963/ijcai.2025/1065},
}

```

📖 **Paper**: [https://arxiv.org/abs/2505.03985](https://doi.org/10.24963/ijcai.2025/1065)

## 📄 License

This project is part of academic research accepted and published at IJCAI 2025.

## 💡 Usage Tips

1. **Start Simple**: Use the provided example files first
2. **Check Logs**: Review `logidebrief.log` for detailed execution info
3. **Validate First**: Use `--validate-only` to check configuration
4. **Test Incrementally**: Test with one protocol at a time
5. **Monitor API Usage**: Track your OpenAI API usage and costs

## 📧 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation and examples
- Review the troubleshooting guide above

---

**Note**: This is a research prototype implementation. Production deployment would require additional security, scalability, and reliability enhancements.
