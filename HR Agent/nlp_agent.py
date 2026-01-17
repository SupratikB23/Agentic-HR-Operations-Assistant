import logging
import time
from knowledge_base import KnowledgeBase
from intent_classifier import IntentClassifier
from llm_interface import LLMInterface
from action_engine import ActionEngine

class NLP_Agent:
    def __init__(self, pdf_path: str):
        self.kb = KnowledgeBase()
        self.classifier = IntentClassifier()
        self.llm = LLMInterface()
        self.action_engine = ActionEngine()
        
        # Phase 1: Ingest
        self.kb.ingest_pdf(pdf_path)
        
    def process_query(self, query: str) -> str:
        # 1. Intent Classification
        intent = self.classifier.classify(query)
        logging.info(f"Query Intent: {intent}")
        
        # 2. Branching
        if intent == "Action":
            # Phase 3 Logic
            return self.action_engine.execute(query)
        
        else:
            # Retrieve
            semantic_chunks = self.kb.query_similarity(query, k=5)
            structured_facts = self.kb.query_structured(query)
            
            # Combine
            context = semantic_chunks + [{"text": f"FACT: {f['fact']}", "page": f["page"]} for f in structured_facts]
            
            # Generate
            # We strictly separate data types as per requirements, sending both to reasoning engine
            response = self.llm.generate_answer(query, context, intent)
            return response
