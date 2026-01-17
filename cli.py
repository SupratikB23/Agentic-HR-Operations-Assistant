import sys
import os
import time
import json
import re
import logging

# --- CONFIGURATION ---
COOLDOWN_SECONDS = 3.0

# SUppress lower-level logs from the agent modules
logging.basicConfig(level=logging.ERROR)

# Ensure we are running from the directory containing this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the HR Agent directory to sys.path to allow imports
hr_agent_path = os.path.join(script_dir, "HR Agent")
if hr_agent_path not in sys.path:
    sys.path.append(hr_agent_path)

try:
    from nlp_agent import NLP_Agent
except ImportError as e:
    print(f"CRITICAL SYSTEM ERROR: Could not import NLP_Agent.\nDetails: {e}")
    sys.exit(1)


class AgentAdapter:
    """
    Adapts the string-based NLP_Agent to a strict Dictionary Contract.
    Enforces format normalization without modifying the core agent.
    """
    def __init__(self, agent: NLP_Agent):
        self._agent = agent

    def run(self, query: str) -> dict:
        """
        Executes query against agent and parses the response into the contract format.
        Returns:
            { "intent": "Action", "json": dict }
            OR
            { "intent": "Policy", "answer": str }
        """
        try:
            raw_response = self._agent.process_query(query)
        except Exception as e:
            # Graceful degradation if agent fails internally
            return {"intent": "Policy", "answer": f"System Error: Agent execution failed temporarily. ({e})"}

        # Strip whitespace for parsing
        cleaned = raw_response.strip()

        # 1. Detect JSON/Action Response
        # We look for a JSON-like structure starting with {
        if "{" in cleaned and "}" in cleaned:
             # Try to find the first '{' and last '}' to extract potential JSON
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            potential_json = cleaned[start:end]
            
            try:
                data = json.loads(potential_json)
                # Success - It is an action
                return {"intent": "Action", "json": data}
            except json.JSONDecodeError:
                # Malformed JSON, fall through to text processing
                pass

        # 2. Process Text/Policy Response
        # The agent output often contains "Intent: ..." headers. We want just the answer.
        
        # Regex to find "Intent: <Tag>"
        intent_match = re.search(r"Intent:\s*(.+)", cleaned)
        intent_tag = intent_match.group(1).strip() if intent_match else "Informational"

        # Regex to extract content after logical separators if present
        # We look for the main content blocks usually separated by lines
        lines = cleaned.split('\n')
        filtered_lines = []
        for line in lines:
            # Remove structural noise
            if "=====" in line or "----" in line or "Intent:" in line or "AGENT RESPONSE" in line:
                continue
            filtered_lines.append(line)
        
        clean_text = "\n".join(filtered_lines).strip()
        
        if not clean_text:
             clean_text = raw_response # Fallback to raw if over-cleaning occurred

        return {"intent": "Policy", "answer": clean_text}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # --- 1. INITIALIZATION ---
    print("Initialize HR Operations Agent...")
    print("Loading Knowledge Base... [Please Wait]")
    
    agent_instance = None
    try:
        # Point to the PDF. 
        pdf_path = os.path.abspath(os.path.join(script_dir, "FULL-Annual-Report-2024-25.pdf"))
        
        if not os.path.exists(pdf_path):
             print(f"\n[!] WARNING: PDF file not found at {pdf_path}")
             print("    Agent will run in limited mode.\n")
        
        # Initialize Agent
        agent_instance = NLP_Agent(pdf_path)
        adapter = AgentAdapter(agent_instance)
        
    except Exception as e:
        print(f"\n[FATAL] Initialization Failed: {e}")
        return

    clear_screen()
    print("==================================================================")
    print("        HR OPERATIONS ENTERPRISE ASSISTANT (CLI v1.0)             ")
    print("==================================================================")
    print(" GUIDELINES:")
    print("  - Type your query naturally (e.g., 'What is the leave policy?')")
    print("  - System enforces a delay between queries for stability.")
    print("  - Type 'exit' or 'quit' to terminate session.")
    print("==================================================================")

    # --- 2. REPL LOOP ---
    last_query = ""
    
    while True:
        try:
            # A. INPUT
            print("\n[READY]")
            user_input = input("HR-CLI >> ").strip()
            
            # B. VALIDATION
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print("Session terminated by user.")
                break
            
            # Anti-Abuse: Deduplication
            if user_input == last_query:
                print("\n[!] DUPLICATE DETECTED: Ignoring repeated query to prevent spam.")
                continue
            
            last_query = user_input
            
            print("... Processing ...")
            
            # C. EXECUTION (Synchronous)
            result = adapter.run(user_input)
            
            # D. RENDERING
            print("\n" + "="*66)
            
            if result.get("intent") == "Action":
                # Strict Rule: JSON ONLY, No Prose
                print("[ACTION PENDING] >> JSON OUTPUT")
                print("-" * 30)
                print(json.dumps(result["json"], indent=2))
                print("-" * 30)
            else:
                # Informational
                print("[?] INFORMATION / POLICY")
                print("-" * 30)
                print(result.get("answer", "No response content."))
            
            print("="*66)
            
            # E. COOLDOWN (Mandatory)
            time.sleep(COOLDOWN_SECONDS)
            
        except KeyboardInterrupt:
            print("\n\n[!] Interrupt Signal Received. Exiting...")
            break
        except Exception as e:
            print(f"\n[!] UNEXPECTED ERROR: {e}")
            # Prevent loop crash, strict recover
            time.sleep(1)
            continue

if __name__ == "__main__":
    main()
