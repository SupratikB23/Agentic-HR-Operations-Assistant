import logging
import time
from typing import List, Dict
from config import OPENAI_API_KEY

class LLMInterface:
    """Mock or Real LLM Interface."""
    def __init__(self):
        self.llm_disabled = False # Flag to disable LLM on rate limit

    def generate_answer(self, query: str, context_chunks: List[Dict], intent: str) -> str:
        
        # Prepare Context
        context_str = "\n\n".join([f"[Page {c['page']}] {c.get('text', c.get('fact', ''))}" for c in context_chunks])
        
        # If API Key is available and not disabled managed by rate limits
        if OPENAI_API_KEY and not self.llm_disabled:
            try:
                from openai import OpenAI
                
                client = OpenAI(
                  base_url="https://openrouter.ai/api/v1",
                  api_key=OPENAI_API_KEY,
                )
                
                system_prompt = f"""
You are an enterprise HR assistant. You must answer heavily based on the provided CONTEXT.
Intent: {intent}
Rules:
1. If intent is 'Policy', cite page numbers [Page X].
2. If intent is 'Action', describe the policy but DO NOT generate JSON here.
3. Be concise and professional.
4. If the answer is NOT in the context, say "I cannot find this information in the documents."
"""
                user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}"
                
                MODELS = [
                    "xiaomi/mimo-v2-flash:free"
                ]

                for model in MODELS:
                    try:
                        logging.info(f"Sending request to OpenRouter (Model: {model})...")
                        
                        # Using the exact call structure requested
                        response = client.chat.completions.create(
                          model=model,
                          messages=[
                                  {
                                    "role": "system", 
                                    "content": system_prompt
                                  },
                                  {
                                    "role": "user", 
                                    "content": user_prompt
                                  }
                                ],
                          # extra_body={"reasoning": {"enabled": True}} # Disabled reasoning to save potential overhead
                        )

                        # Extract the assistant message 
                        message = response.choices[0].message
                        answer = message.content

                        # Success! Log and return (skipping other models)
                        logging.info(f"Model {model} call successful. Returning response.")
                        return f"""
==================================================
AGENT RESPONSE (Generated via OpenRouter: {model})
Intent: {intent}
--------------------------------------------------
{answer}
==================================================
"""
                    except Exception as e:
                        logging.warning(f"Model {model} failed with error: {e}")
                        time.sleep(1) # Short backoff
                        continue
                
                # If loop finishes without return, it means all models failed
                logging.error("All LLM models failed. Falling back to offline mode.\n")
                self.llm_disabled = True # Disable future attempts for this session to save time

            except Exception as e:
                logging.error(f"Global LLM Setup/Execution Error: {e}")
                
        
        # Fallback: Smart Extraction Mode (No LLM)
        # We attempt to extract the most relevant sentence from the top chunks.
        
        if not context_chunks:
            return """
==================================================
AGENT RESPONSE (Offline Mode)
Intent: {}
--------------------------------------------------
**Status:** No relevant information found in the document.
==================================================
""".format(intent)

        # 1. Gather all sentences from evidence
        all_sentences = []
        import re
        for c in context_chunks:
            if 'text' in c:
                clean_text = c['text'].replace('\n', ' ')
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', clean_text)
                for s in sentences:
                    if len(s.strip()) > 10: # Filter noise
                        all_sentences.append({'text': s.strip(), 'page': c['page']})
        
        # 2. Score sentences based on query keywords
        import collections
        query_words = set(re.findall(r'\w+', query.lower())) - {'what', 'is', 'the', 'are', 'for', 'of', 'in', 'to', 'a', 'an', 'rules', 'policy'}
        
        scored_sentences = []
        for s in all_sentences:
            score = 0
            if not s['text']: continue
            s_lower = s['text'].lower()
            
            # Keywork match
            matches = sum(1 for w in query_words if w in s_lower)
            score += matches * 2
            
            # Boost length slightly (prefer substantial sentences)
            if len(s['text']) > 50:
                score += 0.5
                
            if score > 0:
                scored_sentences.append((score, s))
        
        # 3. Sort and Select Top 3
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [x[1] for x in scored_sentences[:3]]
        
        # Formulate "Synthesized" Answer
        synthesized_text = ""
        if top_sentences:
            synthesized_text = "Based on the document analysis, the following relevant policies/facts were found:\n"
            for item in top_sentences:
                synthesized_text += f"> \"{item['text']}\" [Page {item['page']}]\n"
        else:
            # Fallback 2: If no sentences matched keywords well, just dump the top chunk text
            top_chunk = context_chunks[0]
            text_snippet = top_chunk.get('text', '')[:300].replace('\n', ' ')
            synthesized_text = f"Exact sentence match failed, but here is the most relevant section found:\n> \"...{text_snippet}...\" [Page {top_chunk['page']}]"

        evidence_summary = "\n".join([
            f"- [PAGE {c['page']}] ...{c.get('text', '')[:100].replace(chr(10), ' ')}..." 
            for c in context_chunks if 'text' in c
        ])
        
        return f"""
==================================================
AGENT RESPONSE (Offline Mode - Rate Limit/No Key)
Intent: {intent}
--------------------------------------------------
**Synthesized Answer:**
{synthesized_text}

**Evidence Match Summary:**
{evidence_summary}

**Citations:**
{', '.join(sorted(list(set([f"Page {c['page']}" for c in context_chunks]))))}
==================================================
"""
