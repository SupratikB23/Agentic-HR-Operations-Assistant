import json
import re
from datetime import datetime, timedelta

class ActionEngine:
    """
    Deterministic Action Engine for Agentic HR Operations.
    
    Transforms user intents into rigorously defined JSON payloads (Mock Executions).
    Enforces strict schemas for 5 key enterprise actions:
    1. APPLY_LEAVE
    2. RAISE_TICKET
    3. SCHEDULE_MEETING
    4. CLAIM_ALLOWANCE
    5. ESCALATE_TO_HUMAN
    """
    
    def execute(self, query: str) -> str:
        """
        Parses the user query to identify actionable intents and returns a deterministic JSON payload.
        
        Args:
            query (str): The user's natural language input.
            
        Returns:
            str: A JSON string strictly adhering to the defined Agentic Schemas,
                 or a plain text string if the mock engine detects a Forbidden/Informational query.
        """
        query_lower = query.lower().strip()

        # 1. GUARDRAILS
        
        # Forbidden: Approve/Reject Requests
        if any(w in query_lower for w in ["approve", "reject", "authorize"]) and \
           any(w in query_lower for w in ["request", "application", "leave", "expense"]):
             return "I cannot approve requests. Please contact your manager."
        
        # Forbidden: Modify Salary/Contracts
        if any(w in query_lower for w in ["modify", "change", "increase", "decrease", "update"]) and \
           any(w in query_lower for w in ["salary", "contract", "pay", "compensation", "ctc"]):
             return "I cannot modify contracts. Please raise a Payroll ticket."
        
        # Forbidden: View Other's Data
        if "view" in query_lower and any(w in query_lower for w in ["other", "colleague", "employee", "manager", "peer"]):
             return "I can only access your personal records."
             
        # Forbidden: Terminate/Hire
        if any(w in query_lower for w in ["fire", "terminate", "hire", "recruit"]) and \
           not any(w in query_lower for w in ["meeting", "schedule"]): # Exception for scheduling
             return "I cannot perform strategic HR functions like hiring or termination."

        # 2. INTENT DETECTION & MOCK EXECUTION
        
        # ACTION 1: APPLY_LEAVE
        # Workflow: Transactional (Write)
        if any(w in query_lower for w in ["leave", "time off", "vacation", "sick day"]):
            return self._handle_apply_leave(query_lower)
            
        # ACTION 2: RAISE_TICKET
        # Workflow: Support (Track)
        elif any(w in query_lower for w in ["ticket", "issue", "it support", "bug", "software", "laptop", "access", "payroll issue"]):
            return self._handle_raise_ticket(query_lower)
            
        # ACTION 3: SCHEDULE_MEETING
        # Workflow: Coordination (Calendar)
        elif any(w in query_lower for w in ["meeting", "schedule", "calendar", "meet with", "appointment"]):
            return self._handle_schedule_meeting(query_lower)
            
        # ACTION 4: CLAIM_ALLOWANCE
        # Workflow: Policy-Reasoned (Eligibility Check)
        elif any(w in query_lower for w in ["allowance", "reimburse", "claim", "expense", "bill", "stipend"]):
            return self._handle_claim_allowance(query_lower)
        
        # ACTION 5: ESCALATE_TO_HUMAN
        # Workflow: Safety & Fallback
        elif any(w in query_lower for w in ["escalate", "human", "talk to", "person", "representative", "complaint", "frustrated"]):
             return self._handle_escalation(query_lower)

        # Fallback: No Action Detected -> Return strictly generic info intent or let Adapter handle.
        # Returning a safe non-action JSON structure.
        return json.dumps({
            "intent": "Informational",
            "answer": "I can help you Apply Leave, Raise Tickets, Schedule Meetings, Claim Allowances, or Escalate issues. How can I assist?"
        }, indent=2)

    # 3. SHARED DATE PARSING UTILITY
    
    def _parse_date_from_query(self, query_lower, return_range=False):
        """
        Shared intelligent date extraction from natural language.
        
        Args:
            query_lower (str): Lowercase query string
            return_range (bool): If True, returns (start, end) tuple. If False, returns single date.
        
        Returns:
            datetime or tuple: Parsed date(s)
        """
        today = datetime.now()
        start = today + timedelta(days=1)  # Default: tomorrow
        end = start  # Default: single day
        
        # Helper function to get next occurrence of a weekday
        def get_next_weekday(target_day_name):
            """Returns the next occurrence of the specified weekday."""
            days_of_week = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target_day = days_of_week.get(target_day_name.lower())
            if target_day is None:
                return today + timedelta(days=1)
            
            current_day = today.weekday()
            days_ahead = (target_day - current_day) % 7
            if days_ahead == 0:  # If it's today, get next week's occurrence
                days_ahead = 7
            return today + timedelta(days=days_ahead)
        
        # Pattern matching for date extraction
        
        # 1. Check for "next [weekday]"
        next_day_match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', query_lower)
        if next_day_match:
            day_name = next_day_match.group(1)
            start = get_next_weekday(day_name)
            end = start
        
        # 2. Check for "this [weekday]" - closest upcoming occurrence
        elif re.search(r'this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', query_lower):
            this_day_match = re.search(r'this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', query_lower)
            day_name = this_day_match.group(1)
            start = get_next_weekday(day_name)
            end = start
        
        # 3. Check for specific weekday without "next/this"
        elif re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', query_lower):
            weekday_match = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', query_lower)
            day_name = weekday_match.group(1)
            start = get_next_weekday(day_name)
            end = start
        
        # 4. Check for "tomorrow"
        elif "tomorrow" in query_lower:
            start = today + timedelta(days=1)
            end = start
        
        # 5. Check for "today"
        elif "today" in query_lower:
            start = today
            end = start
        
        # 6. Check for "next week"
        elif "next week" in query_lower:
            start = today + timedelta(days=7)
            end = start + timedelta(days=4)  # Assume full week (Mon-Fri)
        
        # 7. Check for "this week"
        elif "this week" in query_lower:
            # Start from next working day
            start = today + timedelta(days=1)
            # End on Friday of current week
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            end = today + timedelta(days=days_until_friday)
        
        # 8. Check for duration (e.g., "3 days", "2 weeks")
        duration_match = re.search(r'(\d+)\s*(day|days|week|weeks)', query_lower)
        if duration_match:
            num = int(duration_match.group(1))
            unit = duration_match.group(2)
            
            if 'week' in unit:
                num *= 7  # Convert weeks to days
            
            # If we haven't set a custom start date yet, use tomorrow
            if start == today + timedelta(days=1) and "tomorrow" not in query_lower:
                # Check if there's a starting reference
                if any(word in query_lower for word in ["from tomorrow", "starting tomorrow"]):
                    start = today + timedelta(days=1)
                elif "from" in query_lower and "next" in query_lower:
                    # Already handled above
                    pass
                else:
                    start = today + timedelta(days=1)
            
            end = start + timedelta(days=num - 1)
        
        # 9. Check for date ranges (e.g., "from Monday to Wednesday")
        from_to_match = re.search(r'from\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+to\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', query_lower)
        if from_to_match:
            start_day = from_to_match.group(1)
            end_day = from_to_match.group(2)
            start = get_next_weekday(start_day)
            end = get_next_weekday(end_day)
            
            # If end is before start, end must be in the following week
            if end <= start:
                end = end + timedelta(days=7)
        
        # 10. Check for time extraction (for meetings)
        time_match = re.search(r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', query_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            meridiem = time_match.group(3)
            
            # Convert to 24-hour format
            if meridiem == 'pm' and hour != 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
            elif not meridiem and hour < 9:  # Assume PM for hours < 9 if no meridiem
                hour += 12
            
            start = start.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end = end.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            # Default meeting time: 10:00 AM
            start = start.replace(hour=10, minute=0, second=0, microsecond=0)
            end = end.replace(hour=10, minute=0, second=0, microsecond=0)
        
        return (start, end) if return_range else start

    # 4. ACTION HANDLERS (Mock Slot Filling)

    def _handle_apply_leave(self, query):
        """Generates payload for APPLY_LEAVE action with intelligent date extraction."""
        # Simple keyword slot mapping
        leave_type = "ANNUAL" # Default
        if "sick" in query: leave_type = "SICK"
        elif "casual" in query: leave_type = "CASUAL"
        
        # Use shared date parser
        start, end = self._parse_date_from_query(query, return_range=True)
        
        # Format dates
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")
        
        reason = "Personal"
        if "sick" in query: reason = "Medical reasons"
        elif "emergency" in query: reason = "Emergency"
        elif "family" in query: reason = "Family matters"
        
        payload = {
            "intent": "Action",
            "json": {
                "action_type": "APPLY_LEAVE",
                "parameters": {
                    "leave_type": leave_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "reason": reason
                },
                "verification": "PENDING_APPROVAL"
            }
        }
        return json.dumps(payload, indent=2)

    def _handle_raise_ticket(self, query):
        """Generates payload for RAISE_TICKET action."""
        category = "IT" # Default
        if "payroll" in query: category = "PAYROLL"
        elif "benefit" in query: category = "BENEFITS"
        
        priority = "NORMAL"
        if any(w in query for w in ["urgent", "critical", "blocking", "immediately"]): 
            priority = "HIGH"
            
        payload = {
            "intent": "Action",
            "json": {
                "action_type": "RAISE_TICKET",
                "parameters": {
                    "category": category,
                    "priority": priority,
                    "subject": "User Reported Issue", # Mock
                    "description": query.replace("raise", "").replace("ticket", "").strip().capitalize() or "User reported issue"
                },
                "verification": "TICKET_CREATED"
            }
        }
        return json.dumps(payload, indent=2)

    def _handle_schedule_meeting(self, query):
        """Generates payload for SCHEDULE_MEETING action with intelligent date/time extraction."""
        department = "HR_BP" # Default
        if "recruit" in query: department = "RECRUITMENT"
        elif "payroll" in query: department = "PAYROLL"
        elif "it" in query: department = "IT"
        
        # Use shared date parser
        meeting_datetime = self._parse_date_from_query(query, return_range=False)
        meeting_str = meeting_datetime.isoformat()
        
        # Extract topic if possible
        topic = "Discussion on " + ("Recruitment" if department == "RECRUITMENT" else "HR Policies")
        if "about" in query:
            about_match = re.search(r'about\s+(.+?)(?:\s+on|\s+at|$)', query)
            if about_match:
                topic = about_match.group(1).strip().capitalize()
        
        payload = {
            "intent": "Action",
            "json": {
                "action_type": "SCHEDULE_MEETING",
                "parameters": {
                    "department": department,
                    "date_time": meeting_str,
                    "topic": topic
                },
                "verification": "SLOT_BOOKED"
            }
        }
        return json.dumps(payload, indent=2)

    def _handle_claim_allowance(self, query):
        """Generates payload for CLAIM_ALLOWANCE action with Policy Logic."""
        category = "RELOCATION" # Default
        if "internet" in query: category = "INTERNET"
        elif "education" in query: category = "EDUCATION"
        
        # Mock Amount Extraction
        amount = 0
        amount_match = re.search(r'\d+', query)
        if amount_match:
            amount = int(amount_match.group())
            
        # Policy Check Mock Logic
        eligible = True
        reason = "Within policy limits"
        
        if category == "RELOCATION" and amount > 5000:
            # eligible = False # For now, let's allow it but warn, or strictly stick to boolean
            reason = "Warning: High amount, requires secondary approval"
            
        payload = {
            "intent": "Action",
            "json": {
                "action_type": "CLAIM_ALLOWANCE",
                "parameters": {
                    "category": category,
                    "amount": amount,
                    "justification": f"Reimbursement for {category.lower()}"
                },
                "policy_check": {
                    "eligible": eligible,
                    "reason": reason
                }
            }
        }
        return json.dumps(payload, indent=2)

    def _handle_escalation(self, query):
        """Generates payload for ESCALATE_TO_HUMAN action."""
        urgency = "NORMAL"
        if any(w in query for w in ["urgent", "anger", "frustrated", "immediately"]):
            urgency = "HIGH"
            
        payload = {
            "intent": "Action",
            "json": {
                "action_type": "ESCALATE_TO_HUMAN",
                "parameters": {
                    "reason": "COMPLEXITY", # Default
                    "summary": "User requested escalation or expressed frustration.",
                    "urgency": urgency
                },
                "verification": "HUMAN_HANDOFF"
            }
        }
        return json.dumps(payload, indent=2)
