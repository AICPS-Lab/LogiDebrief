from openai import OpenAI
import json
import time
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def submit_message(assistant_id, thread, user_message, client):
    """Submit a message to an OpenAI assistant thread."""
    try:
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message
        )
        return client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
    except Exception as e:
        logger.error(f"Error submitting message: {e}")
        raise


def wait_on_run(run, thread, client, max_wait_time=60):
    """Wait for an assistant run to complete with timeout."""
    start_time = time.time()
    while run.status == "queued" or run.status == "in_progress":
        if time.time() - start_time > max_wait_time:
            logger.warning(f"Run timeout after {max_wait_time} seconds")
            raise TimeoutError(f"Assistant run timed out after {max_wait_time} seconds")
        
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.1)
    
    if run.status == "failed":
        logger.error(f"Run failed with error: {run.last_error}")
        raise RuntimeError(f"Assistant run failed: {run.last_error}")
    
    return run


def get_response(thread, client):
    """Retrieve messages from an assistant thread."""
    try:
        return client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    except Exception as e:
        logger.error(f"Error getting response: {e}")
        raise


class FunctionAgents(object):
    def __init__(self, api_key: Optional[str] = None, function_mappings_path: Optional[str] = None):
        """Initialize FunctionAgents with API key and mappings.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            function_mappings_path: Path to function mappings JSON file
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.api_key)
        
        # Load function mappings
        mappings_path = function_mappings_path or Path(__file__).parent.parent / "function_mappings.json"
        try:
            with open(mappings_path, 'r') as f:
                self.function_map = json.load(f)
            logger.info(f"Loaded function mappings from {mappings_path}")
        except FileNotFoundError:
            logger.error(f"Function mappings file not found: {mappings_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in function mappings: {e}")
            raise
        
        self.conversation = None

    def load_conversation(self, conversation):
        self.conversation = conversation

    def validate_address(self):
        """Validate address information from the conversation."""
        return self._call_assistant('address', self.conversation)

    def validate_name(self):
        """Validate name information from the conversation."""
        return self._call_assistant('name', self.conversation)

    def validate_phone(self):
        """Validate phone number information from the conversation."""
        return self._call_assistant('phone', self.conversation)

    def validate_general_check(self, general_check):
        """Validate a general check against the conversation."""
        message = f"check: {general_check}, \n conversation: {self.conversation}"
        return self._call_assistant('general', message)

    def validate_context(self):
        """Validate context flags from the conversation."""
        return self._call_assistant('flags', self.conversation)

    def validate_precondition(self, precondition):
        """Validate preconditions against the conversation."""
        message = f"assertion: {precondition}, \n conversation: {self.conversation}"
        return self._call_assistant('condition', message)

    def validate_check(self, check):
        """Validate a specific check against the conversation."""
        message = f"check: {check}, \n conversation: {self.conversation}"
        return self._call_assistant('check', message)
    
    def _call_assistant(self, assistant_type: str, message: str) -> Dict[str, Any]:
        """Generic method to call an OpenAI assistant with error handling.
        
        Args:
            assistant_type: Type of assistant to call (key in function_map)
            message: Message to send to the assistant
            
        Returns:
            Parsed JSON response from the assistant
        """
        if not self.conversation and assistant_type not in ['general', 'condition', 'check']:
            raise ValueError("No conversation loaded. Call load_conversation() first.")
        
        cur_thread = None
        try:
            # Create thread
            cur_thread = self.openai_client.beta.threads.create()
            
            # Get assistant
            assistant_id = self.function_map.get(assistant_type)
            if not assistant_id:
                raise ValueError(f"No assistant ID found for type: {assistant_type}")
            
            assistant = self.openai_client.beta.assistants.retrieve(assistant_id=assistant_id)
            
            # Submit message and wait for response
            run = submit_message(assistant.id, cur_thread, message, client=self.openai_client)
            wait_on_run(run, cur_thread, client=self.openai_client)
            
            # Get response
            response = get_response(cur_thread, self.openai_client)
            
            # Parse response
            js_output = {}
            for msg in response:
                if msg.role == "assistant":
                    try:
                        js_output = json.loads(msg.content[0].text.value)
                    except (json.JSONDecodeError, IndexError, AttributeError) as e:
                        logger.error(f"Failed to parse assistant response: {e}")
                        logger.debug(f"Raw response: {msg.content}")
                        raise ValueError(f"Invalid response from assistant: {e}")
            
            return js_output
            
        except Exception as e:
            logger.error(f"Error calling assistant {assistant_type}: {e}")
            raise
        finally:
            # Clean up thread
            if cur_thread:
                try:
                    self.openai_client.beta.threads.delete(cur_thread.id)
                except Exception as e:
                    logger.warning(f"Failed to delete thread: {e}")
