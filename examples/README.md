# Example Files for LogiDebrief

This directory contains sample data files for testing the LogiDebrief system.

## Files

### sample_conversation.txt
A sample 911 call transcript demonstrating a medical emergency (abdominal pain). This transcript includes:
- Proper address verification
- Phone number collection
- Caller name identification
- Medical questioning following emergency protocols
- Pre-arrival instructions

### sample_task.json
Configuration file that corresponds to the sample conversation, including:
- Incident type (must match a directory in `/guidecards/`)
- Address and supplementary details
- Service requirements (PD, FD, EMD)
- Optional metadata

## Usage

To run LogiDebrief with these example files:

```bash
# Using the --example flag (easiest)
python main.py --example

# Or specify the files explicitly
python main.py --conversation examples/sample_conversation.txt --task examples/sample_task.json

# To save output to a specific location
python main.py --example --output results/example_output.json
```

## Creating Your Own Examples

1. **Conversation File**: Create a plain text file with the transcript of the emergency call
   - Format: `Role: Message` on each line
   - Roles should be "Dispatcher" or "Caller"

2. **Task Configuration**: Create a JSON file with:
   - `incident_spec.incident_type`: Must match a directory name in `/guidecards/`
   - `incident_spec.address`: The incident address
   - Service flags: `PD` (Police), `FD` (Fire), `EMD` (Emergency Medical)

## Available Incident Types

Check the `/guidecards/` directory for available incident types. Currently includes:
- Abdominal or Back Pain

## Notes

- Ensure your OpenAI API key is configured in the `.env` file
- Assistant IDs must be properly configured in `function_mappings.json`
- The system will validate all inputs before processing