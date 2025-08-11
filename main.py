from functions import FunctionAgents
import os
import json
import logging
import argparse
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on system environment variables

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logidebrief.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def relaxation(boolean_list, x):
    """
    Check if the number of False values in the list is fewer than x.

    Parameters:
        - boolean_list (list): A list of boolean values.
        - x (int): Threshold for the number of False values.

    Returns:
        - True if the number of False values is fewer than x, otherwise False.
    """
    false_count = sum(1 for b in boolean_list if not b)  # Count the False values
    return false_count < x


def get_satisfied_values(applied_conditions, json_data):
    """
    Retrieve all 'i' or 'q' values from the JSON data where the condition 'c' evaluates to True
    against the given list of applied conditions. If 'c' is null, the value always applies.

    Parameters:
    - applied_conditions: A list or set of integers representing satisfied conditions.
    - json_data: The JSON data as a list of dictionaries, or a path to a JSON file.

    Returns:
    - A list of satisfied 'i' or 'q' values.
    """
    import json

    # If json_data is a file path, load the data from the file
    if isinstance(json_data, str):
        with open(json_data, 'r') as file:
            data = json.load(file)
    else:
        data = json_data  # Assume json_data is already loaded as a list of dictionaries

    # Ensure applied_conditions is a set for efficient lookup
    if not isinstance(applied_conditions, set):
        applied_conditions = set(applied_conditions)

    # Function to evaluate condition logic
    def evaluate_condition(condition_logic, applied_conditions):
        def eval_logic(expr):
            expr = expr.strip()
            if expr.startswith("NOT(") and expr.endswith(")"):
                return not eval_logic(expr[4:-1])
            elif expr.startswith("AND(") and expr.endswith(")"):
                sub_exprs = split_expressions(expr[4:-1])
                return all(eval_logic(sub) for sub in sub_exprs)
            elif expr.startswith("OR(") and expr.endswith(")"):
                sub_exprs = split_expressions(expr[3:-1])
                return any(eval_logic(sub) for sub in sub_exprs)
            else:
                # Handle integer conditions
                return int(expr) in applied_conditions

        # Helper function to split expressions, accounting for nested parentheses
        def split_expressions(s):
            expressions = []
            bracket_level = 0
            last_index = 0
            for index, char in enumerate(s):
                if char == '(':
                    bracket_level += 1
                elif char == ')':
                    bracket_level -= 1
                elif char == ',' and bracket_level == 0:
                    expressions.append(s[last_index:index].strip())
                    last_index = index + 1
            expressions.append(s[last_index:].strip())
            return expressions

        return eval_logic(condition_logic)

    # Retrieve all 'i' or 'q' values where condition 'c' evaluates to True or 'c' is null
    satisfied_values = []
    for item in data:
        condition = item.get('c')  # Retrieve the condition
        if condition is None or condition.strip() == "":  # Apply unconditionally
            value = item.get('i') or item.get('q')
            if value:
                satisfied_values.append(value)
        else:
            # Evaluate the condition logic
            if evaluate_condition(condition, applied_conditions):
                value = item.get('i') or item.get('q')
                if value:
                    satisfied_values.append(value)

    return satisfied_values


def debrief_init(functions: FunctionAgents, conversation: str, task_json: Dict[str, Any]) -> Dict[str, Any]:
    """Initial debrief function (legacy version).
    
    Args:
        functions: FunctionAgents instance
        conversation: Conversation transcript text
        task_json: Task configuration dictionary
        
    Returns:
        Dictionary containing debrief results
    """
    logger.info("Starting debrief_init function...")
    functions.load_conversation(conversation)

    out_json = {
        "Call-taker obtained and verified the address": {
            "asked address first": None,
            "address double checking": None,
            "obtained address": None,
            "double check at the end": None,
            "result": None,
            "explanation": None
        },

        "Call-taker obtained and verified caller's phone": {
            "ask for phone number": None,
            "phone number follow up": None,
            "obtained phone number": None,
            "result": None,
            "explanation": None
        },

        "Call-taker obtained and verified caller's full name":{
            "ask for full name": None,
            "full name follow up": None,
            "obtained full name": None,
            "result": None,
            "explanation": None
        },

        "Call-taker asked what is the problem?":{
            "result": None,
            "explanation": None
        },

        "Call-taker questioned about the number of injured persons?":{
            "result": None,
            "explanation": None
        },

        "Call-taker asked for age of patient(s)?":{
            "result": None,
            "explanation": None
        },

        "Call-taker asked if the patient(s) conscious?":{
            "result": None,
            "explanation": None
        },

        "Call-taker asked if the patient(s) breathing normally?":{
            "result": None,
            "explanation": None
        },

        "Call-taker used guidecards to obtain additional information?": {
            "result": None,
            "explanation": None
        },

        "Call-taker used guidecards to provide prearrival instructions?": {
            "result": None,
            "explanation": None
        },

        "Call-taker used guide cards to provide Time / Life Critical Instructions?": {
            "result": None,
            "explanation": None
        },

        "Call-taker obtained scene safety / suspect information?": {
            "result": None,
            "explanation": None
        }
    }


    address_check_return = functions.validate_address()
    out_json["Call-taker obtained and verified the address"] = {
        "asked address first": address_check_return["ask-first"],
        "address double checking": address_check_return["address-confirmation"],
        "obtained address": address_check_return["obtained-address"],
        "double check at the end": address_check_return["double-checking-end"],
        "result": address_check_return['overall-eval'],
        "explanation": address_check_return['explanations']
    }
    logger.debug(f"Address validation result: {address_check_return}")

    phone_check_return = functions.validate_phone()
    out_json["Call-taker obtained and verified caller's phone"] = {
        "asked phone number": phone_check_return["ask-phone-number"],
        "phone number follow up": phone_check_return["phone-follow-up"],
        "obtained phone number": phone_check_return["obtained-phone"],
        "result": phone_check_return['overall-eval'],
        "explanation": phone_check_return['explanations']
    }
    logger.debug(f"Phone validation result: {phone_check_return}")
    #
    name_check_return = functions.validate_name()
    out_json["Call-taker obtained and verified caller's full name"] = {
        "asked full name": name_check_return["ask-full-name"],
        "full name follow up": name_check_return["name-follow-up"],
        "obtained full name": name_check_return["obtained-name"],
        "result": name_check_return['overall-eval'],
        "explanation": name_check_return['explanations']
    }
    logger.debug(f"Name validation result: {name_check_return}")

    general_checks = [
        "Call-taker asked what is the problem?",
        "Call-taker questioned about the number of injured persons?",
        "Call-taker asked for age of patient(s)?",
        "Call-taker asked if the patient(s) conscious?",
        "Call-taker asked if the patient(s) breathing normally?",
        "Call-taker obtained scene safety / suspect information?"
    ]
    for gc in general_checks:
        if gc == "Call-taker obtained scene safety / suspect information":
            temp_gc = "If the scene is potentially dangerous to first responders, call-taker obtained scene safety / suspect information"
            out_json[gc] = {
                "result": functions.validate_general_check(temp_gc)['result'],
                "explanation": functions.validate_general_check(temp_gc)['explanations']
            }
        else:
            out_json[gc] = {
                "result": functions.validate_general_check(gc)['result'],
                "explanation": functions.validate_general_check(gc)['explanations']
            }

    logger.debug(f"General checks completed")

    flags_return = functions.validate_context()
    critical_flags = flags_return['flags']
    critical_explanations = flags_return['explanations']

    out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["explanation"] = critical_explanations
    if critical_flags and critical_flags[0] in ["AC", "AED", "BTA", "CB", "CPR", "OA"]:
        file_path = os.path.join(f"./protocols/{critical_flags[0]}/", "conditions.json")
        # print(file_path)
        with open(file_path, "r") as file:
            critical_conditions = json.load(file)
    #
        condition_return = functions.validate_precondition(critical_conditions)
        applied_conditions = condition_return['result']
        applied_condition_explanation = condition_return['explanations']
        out_json["Call-taker used guidecards to obtain additional information?"]["explanation"] = applied_condition_explanation
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["explanation"] = applied_condition_explanation
        # print(applied_conditions)

        instructions_path = os.path.join(f"./protocols/{critical_flags[0]}/", "instructions.json")
        with open(instructions_path, "r") as file:
            all_instructions = json.load(file)

        applied_instructions = get_satisfied_values(applied_conditions, all_instructions)
        # print(applied_instructions)

        session_instruction_check = []
        for ai in applied_instructions:
            session_instruction_check.append(functions.validate_check(ai)['result'])

        # print(session_instruction_check)

        if len(session_instruction_check) == 0:
            out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["result"] = "N/A"
        elif relaxation(session_instruction_check,int(0.0 * (len(applied_instructions)))):
            out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["result"] = "YES"
            out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["explanation"] += "Applied instructions are necessarily given."

        elif False in session_instruction_check:
            false_index = session_instruction_check.index(False)
            out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["result"] = "NO"
            out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["explanation"] += f"Applied instructions are not necessarily given, e.g., {applied_instructions[false_index]}."
    else:
        out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["result"] = "N/A"

    logger.info("Critical instructions check: %s", 
                out_json["Call-taker used guide cards to provide Time / Life Critical Instructions?"]["result"])

    incident_type = task_json["incident_spec"]["incident_type"]
    questions_path = os.path.join(f"./guidecards/{incident_type}/", "questions.json")
    prearrivals_path = os.path.join(f"./guidecards/{incident_type}/", "instructions.json")
    conditions_path = os.path.join(f"./guidecards/{incident_type}/", "conditions.json")


    with open(conditions_path, "r") as file:
        all_conditions = json.load(file)

    applied_conditions = functions.validate_precondition(all_conditions)['result']
    # print(applied_conditions)
    out_json["Call-taker used guidecards to obtain additional information?"]["explanation"] = functions.validate_precondition(all_conditions)['explanations']
    out_json["Call-taker used guidecards to provide prearrival instructions?"]["explanation"] = functions.validate_precondition(all_conditions)['explanations']
    with open(questions_path, "r") as file:
        all_questions = json.load(file)

    applied_questions = get_satisfied_values(applied_conditions, all_questions)

    session_question_check = []
    for aq in applied_questions:
        session_question_check.append(functions.validate_check(aq))

    if len(session_question_check) == 0:
        out_json["Call-taker used guidecards to obtain additional information?"]["result"] = "N/A"
    elif relaxation(session_question_check,int(0.0 * (len(applied_questions)))):
        out_json["Call-taker used guidecards to obtain additional information?"]["result"] = "YES"
        out_json["Call-taker used guidecards to obtain additional information?"]["explanation"] += "Applied instructions are necessarily given."

    elif False in session_question_check:
        false_index = session_question_check.index(False)
        out_json["Call-taker used guidecards to obtain additional information?"]["result"] = "NO"
        out_json["Call-taker used guidecards to obtain additional information?"]["explanation"] += f"Applied instructions are not necessarily given, e.g., {applied_questions[false_index]}."

    logger.info("Additional information check: %s",
                out_json["Call-taker used guidecards to obtain additional information?"]["result"])

    with open(prearrivals_path, "r") as file:
        all_prearrivals = json.load(file)

    applied_prearrivals = get_satisfied_values(applied_conditions, all_prearrivals)
    session_prearrivals_check = []
    for ap in applied_prearrivals:
        session_prearrivals_check.append(functions.validate_check(ap))

    if len(session_question_check) == 0:
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["result"] = "N/A"
    elif relaxation(session_question_check,int(0.0 * (len(applied_questions)))):
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["result"] = "YES"
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["explanation"] += "Applied instructions are necessarily given."

    elif False in session_question_check:
        false_index = session_question_check.index(False)
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["result"] = "NO"
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["explanation"] += f"Applied instructions are not necessarily given, e.g., {applied_prearrivals[false_index]}."

    logger.info("Prearrival instructions check: %s",
                out_json["Call-taker used guidecards to provide prearrival instructions?"]["result"])

    with open("out.json", "w") as jfile:
        json.dump(out_json, jfile, indent=4)

    return out_json


current_dir = os.path.dirname(__file__)


def debrief(functions: FunctionAgents, conversation: str, task_json: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized debrief function with parallel processing.
    
    Args:
        functions: FunctionAgents instance
        conversation: Conversation transcript text
        task_json: Task configuration dictionary
        
    Returns:
        Dictionary containing debrief results
    """
    logger.info("Starting debrief function...")
    functions.load_conversation(conversation)
    logger.debug("Conversation loaded into functions.")

    # Initialize output JSON structure
    out_json = {
        "Call-taker obtained and verified the address": {},
        "Call-taker obtained and verified caller's phone": {},
        "Call-taker obtained and verified caller's full name": {},
        "Call-taker asked what is the problem?": {},
        "Call-taker questioned about the number of injured persons?": {},
        "Call-taker asked for age of patient(s)?": {},
        "Call-taker asked if the patient(s) conscious?": {},
        "Call-taker asked if the patient(s) breathing normally?": {},
        "Call-taker used guidecards to obtain additional information?": {
            "result": "N/A",
            "explanation": ""
        },
        "Call-taker used guidecards to provide prearrival instructions?": {
            "result": "N/A",
            "explanation": ""
        },
        "Call-taker used guide cards to provide Time / Life Critical Instructions?": {
            "result": "N/A",
            "explanation": ""
        },
        "Call-taker obtained scene safety / suspect information?": {},
        "applied_questions": [],
        "not_applied_questions": [],
        "applied_prearrivals": [],
        "not_applied_prearrivals": [],
        "applied_protocols": [],
        "not_applied_protocols": []
    }

    def validate_address():
        logger.debug("Validating address...")
        result = functions.validate_address()
        return {
            "asked address first": result["ask-first"],
            "address double checking": result["address-confirmation"],
            "obtained address": result["obtained-address"],
            "double check at the end": result["double-checking-end"],
            "result": result['overall-eval'],
            "explanation": result['explanations']
        }

    def validate_phone():
        logger.debug("Validating phone...")
        result = functions.validate_phone()
        return {
            "ask for phone number": result["ask-phone-number"],
            "phone number follow up": result["phone-follow-up"],
            "obtained phone number": result["obtained-phone"],
            "result": result['overall-eval'],
            "explanation": result['explanations']
        }

    def validate_name():
        logger.debug("Validating name...")
        result = functions.validate_name()
        return {
            "ask for full name": result["ask-full-name"],
            "full name follow up": result["name-follow-up"],
            "obtained full name": result["obtained-name"],
            "result": result['overall-eval'],
            "explanation": result['explanations']
        }

    def validate_general_check(check):
        logger.debug(f"Validating general check: {check}")
        return check, functions.validate_general_check(check)

    def validate_flags():
        logger.debug("Validating flags...")
        return functions.validate_context()

    def process_guidecard_checks(conditions, questions, prearrivals):
        logger.debug("Processing guidecard checks...")
        condition_return = functions.validate_precondition(conditions)
        applied_conditions = condition_return['result']
        explanation = condition_return['explanations']
        out_json["Call-taker used guidecards to obtain additional information?"]["explanation"] = explanation
        out_json["Call-taker used guidecards to provide prearrival instructions?"]["explanation"] = explanation

        applied_questions = get_satisfied_values(applied_conditions, questions)
        applied_prearrivals = get_satisfied_values(applied_conditions, prearrivals)

        with ThreadPoolExecutor() as executor:
            question_futures = {
                executor.submit(functions.validate_check, question): question for question in applied_questions
            }
            prearrival_futures = {
                executor.submit(functions.validate_check, prearrival): prearrival for prearrival in applied_prearrivals
            }

            session_question_check = []
            session_prearrivals_check = []

            for future in as_completed(question_futures):
                question = question_futures[future]
                try:
                    result = future.result()['result']
                    session_question_check.append(result)
                    if result:
                        out_json["applied_questions"].append(question)
                    else:
                        out_json["not_applied_questions"].append(question)
                except Exception as e:
                    logger.error(f"Error validating question {question}: {e}")
                    session_question_check.append(False)

            for future in as_completed(prearrival_futures):
                prearrival = prearrival_futures[future]
                try:
                    result = future.result()['result']
                    session_prearrivals_check.append(result)
                    if result:
                        out_json["applied_prearrivals"].append(prearrival)
                    else:
                        out_json["not_applied_prearrivals"].append(prearrival)
                except Exception as e:
                    logger.error(f"Error validating prearrival {prearrival}: {e}")
                    session_prearrivals_check.append(False)

        return session_question_check, session_prearrivals_check

    general_checks = [
        "Call-taker asked what is the problem?",
        "Call-taker questioned about the number of injured persons?",
        "Call-taker asked for age of patient(s)?",
        "Call-taker asked if the patient(s) conscious?",
        "Call-taker asked if the patient(s) breathing normally?",
        "Call-taker obtained scene safety / suspect information?"
    ]

    with ThreadPoolExecutor() as executor:
        logger.debug("Starting parallel tasks...")

        # Start address, phone, name validations in parallel
        address_future = executor.submit(validate_address)
        phone_future = executor.submit(validate_phone)
        name_future = executor.submit(validate_name)

        # Start general checks validation in parallel
        general_checks_futures = {executor.submit(validate_general_check, check): check for check in general_checks}

        # Validate flags first (dependency for instructions)
        logger.debug("Waiting for flags validation...")
        flags_result = validate_flags()
        logger.debug("Flags validated.")
        critical_flags = flags_result['flags']
        if critical_flags:
            out_json["applied_protocols"].extend(critical_flags)
        else:
            out_json["not_applied_protocols"].append("No critical flags detected.")

        # Read guidecard files after flags are checked
        incident_type = task_json["incident_spec"]["incident_type"]
        with open(os.path.join(current_dir, "guidecards", incident_type, "conditions.json"), "r") as file:
            conditions = json.load(file)
        with open(os.path.join(current_dir, "guidecards", incident_type, "questions.json"), "r") as file:
            questions = json.load(file)
        with open(os.path.join(current_dir, "guidecards", incident_type, "instructions.json"), "r") as file:
            prearrivals = json.load(file)

        # Process guidecard-related checks
        session_question_check, session_prearrivals_check = process_guidecard_checks(conditions, questions, prearrivals)

        # Collect results for address, phone, name
        logger.debug("Waiting for address, phone, and name validations...")
        out_json["Call-taker obtained and verified the address"] = address_future.result()
        out_json["Call-taker obtained and verified caller's phone"] = phone_future.result()
        out_json["Call-taker obtained and verified caller's full name"] = name_future.result()
        logger.debug("Address, phone, and name validations completed.")

        # Process general checks
        logger.debug("Processing general checks...")
        for future in as_completed(general_checks_futures):
            check, result = future.result()
            out_json[check] = result

    logger.info("Debrief function completed successfully.")
    return out_json


def main():
    """Main entry point for the LogiDebrief application."""
    parser = argparse.ArgumentParser(
        description='LogiDebrief: Automated debriefing for emergency call transcripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --conversation transcript.txt --task task_config.json
  python main.py --conversation examples/sample_conversation.txt --task examples/sample_task.json
  python main.py --example  # Run with example data
        """
    )
    
    parser.add_argument(
        '--conversation', '-c',
        type=str,
        help='Path to conversation transcript file'
    )
    parser.add_argument(
        '--task', '-t',
        type=str,
        help='Path to task configuration JSON file'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='out.json',
        help='Output file path (default: out.json)'
    )
    parser.add_argument(
        '--example',
        action='store_true',
        help='Run with example data from examples/ directory'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration without running debrief'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize function agents
        logger.info("Initializing FunctionAgents...")
        functions = FunctionAgents()
        
        # Validate configuration
        if args.validate_only:
            logger.info("Configuration validated successfully.")
            return 0
        
        # Determine input files
        if args.example:
            # Use example files
            examples_dir = Path(__file__).parent / 'examples'
            conversation_path = examples_dir / 'sample_conversation.txt'
            task_path = examples_dir / 'sample_task.json'
            
            if not conversation_path.exists() or not task_path.exists():
                logger.error("Example files not found. Please create them in the examples/ directory.")
                return 1
        else:
            # Use provided files
            if not args.conversation or not args.task:
                parser.error("--conversation and --task are required unless using --example")
            
            conversation_path = Path(args.conversation)
            task_path = Path(args.task)
        
        # Validate input files exist
        if not conversation_path.exists():
            logger.error(f"Conversation file not found: {conversation_path}")
            return 1
        
        if not task_path.exists():
            logger.error(f"Task configuration file not found: {task_path}")
            return 1
        
        # Load input data
        logger.info(f"Loading conversation from: {conversation_path}")
        with open(conversation_path, 'r') as f:
            conversation = f.read()
        
        logger.info(f"Loading task configuration from: {task_path}")
        with open(task_path, 'r') as f:
            task_json = json.load(f)
        
        # Validate task JSON structure
        required_fields = ['incident_spec']
        incident_fields = ['incident_type']
        
        for field in required_fields:
            if field not in task_json:
                logger.error(f"Missing required field in task JSON: {field}")
                return 1
        
        for field in incident_fields:
            if field not in task_json['incident_spec']:
                logger.error(f"Missing required field in incident_spec: {field}")
                return 1
        
        # Run debrief
        logger.info("Starting debrief process...")
        result = debrief(functions, conversation, task_json)
        
        # Save output
        output_path = Path(args.output)
        logger.info(f"Saving results to: {output_path}")
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=4)
        
        logger.info("Debrief completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())