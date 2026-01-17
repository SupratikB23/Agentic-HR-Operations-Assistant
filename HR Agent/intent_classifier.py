class IntentClassifier:
    def classify(self, query: str) -> str:
        """Classifies intent: Informational, Policy, Comparative, Action."""
        q = query.lower()
        if any(w in q for w in ["apply", "schedule", "book", "raise", "create"]):
            return "Action"
        elif any(w in q for w in ["compare", "difference", "versus", "vs", "trend", "growth"]):
            return "Comparative"
        elif any(w in q for w in ["policy", "eligible", "allowed", "rule", "exception", "can i"]):
            return "Policy"
        else:
            return "Informational"
