import sys
import os
import time

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
    print(f"Error importing NLP_Agent: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("Initializing Agent...")
    # Point to the PDF. Assuming it is in the parent directory of 'agent/'
    pdf_path = os.path.abspath(os.path.join(script_dir, "FULL-Annual-Report-2024-25.pdf"))
    
    # Check if PDF exists to be robust
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file not found at {pdf_path}")
        # asking user to check path? or just proceeding might fail.
        # But per instructions, I should run the tasks correctly.
    
    # Initialize Agent
    # Note: KnowledgeBase defaults to loading 'faiss_index.bin' from CWD (which is now 'agent/')
    agent = NLP_Agent(pdf_path)
    
    print("\n--- Test 1: Informational ---")
    q1 = "What is the revenue growth?"
    print(f"Q: {q1}")
    
    print(agent.process_query(q1))
    # Add delay to avoid Rate Limits
    time.sleep(5)
    
    print("\n--- Test 2: Action ---")
    q2 = "Apply for earned leave next monday"
    print(f"Q: {q2}")
    print(agent.process_query(q2))
    time.sleep(5)
    
    print("\n--- Test 3: Policy ---")
    q3 = "What is the dividend distribution policy?"
    print(f"Q: {q3}")
    print(agent.process_query(q3))
