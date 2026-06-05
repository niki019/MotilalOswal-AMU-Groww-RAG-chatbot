import os
import re
import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')
from groq import Groq
from rag_engine import RAGEngine

# Set up default Groq model
DEFAULT_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"

class FAQChatbot:
    def __init__(self):
        self.rag = RAGEngine()
        # Set Groq API key from environment, fallback to the user's provided key if not set
        self.api_key = os.environ.get("GROQ_API_KEY")
        
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: GROQ_API_KEY is not set. Chatbot will run in offline/fallback mode.")

    def is_advisory_query(self, query):
        """
        Classifies if a query is advisory or seeks opinions/speculation.
        Uses rule-based heuristics first, and falls back to Groq classification.
        """
        query_lower = query.lower().strip()
        
        # Static heuristic triggers
        advisory_keywords = [
            "should i invest", "should i buy", "which is better", "which fund is better",
            "is it good to invest", "recommend", "advice", "opinion", "better investment",
            "suggest a fund", "help me choose", "predict returns", "will it grow",
            "is this fund safe", "worth investing"
        ]
        if any(kw in query_lower for kw in advisory_keywords):
            return True

        if not self.client:
            # Offline fallback
            return False

        # LLM Classifier using Groq Llama 3
        prompt = (
            "Classify the following user query about mutual funds into one of two categories: 'FACTUAL' or 'ADVISORY'.\n"
            "- 'FACTUAL': Seeking objective, verifiable facts, details, numbers, or processes (e.g., 'What is the NAV of X?', 'Who manages Y?', 'How do I download statement?').\n"
            "- 'ADVISORY': Seeking advice, recommendations, opinions, comparative comparisons, future returns prediction, or suitability (e.g., 'Should I invest in X?', 'Which fund is better?', 'Will it double my money?').\n\n"
            f"Query: \"{query}\"\n\n"
            "Response with exactly one word (either FACTUAL or ADVISORY):"
        )
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=DEFAULT_MODEL,
                temperature=0.0
            )
            result = response.choices[0].message.content.strip().upper()
            return "ADVISORY" in result
        except Exception as e:
            print(f"Error classifying query via Groq: {e}. Trying fallback model...")
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=FALLBACK_MODEL,
                    temperature=0.0
                )
                result = response.choices[0].message.content.strip().upper()
                return "ADVISORY" in result
            except Exception as e2:
                print(f"Error classifying with fallback model: {e2}")
                return False

    def generate_advisory_refusal(self):
        """
        Returns a polite refusal response for advisory queries.
        """
        return (
            "I am a facts-only assistant and cannot provide investment advice, recommendations, or opinions. "
            "For reliable educational resources and guidance, please visit the official "
            "[AMFI Investor Education Portal](https://www.amfiindia.com/investor-corner/education) or "
            "[SEBI Investor Education](https://investor.sebi.gov.in/)."
        )

    def clean_sentence_count(self, text, max_sentences=3):
        """
        Post-processing constraint guardrail:
        Truncates the response to at most max_sentences if the model exceeded it.
        """
        # Split sentences avoiding common abbreviations (Mr., Mrs., Dr., Ltd., Cr., etc.)
        pattern = r'(?<!\b[Mm]r\.)(?<!\b[Mm]rs\.)(?<!\b[Dd]r\.)(?<!\b[Mm]s\.)(?<!\b[Ll]td\.)(?<!\b[Cc]o\.)(?<!\b[Cc]r\.)(?<!\b[Ee]\.[Gg]\.)(?<!\b[Ii]\.[Ee]\.)(?<=[.!?])\s+'
        sentences = re.split(pattern, text.strip())
        if len(sentences) <= max_sentences:
            return text
        return " ".join(sentences[:max_sentences])

    def validate_citation(self, text, source_url):
        """
        Post-processing constraint guardrail:
        Ensures exactly one markdown hyperlink pointing to the source url.
        """
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        
        # If no links are present, append the citation link
        if not links:
            return f"{text} Source details can be found on [Groww]({source_url})."
            
        # If multiple links exist, keep only the first valid one and strip others
        if len(links) > 1:
            cleaned_text = text
            for link_text, link_url in links:
                cleaned_text = cleaned_text.replace(f"[{link_text}]({link_url})", link_text)
            return f"{cleaned_text} (Source: [{links[0][0]}]({links[0][1]}))"
            
        return text

    def detect_pii(self, query):
        """
        Detects if the query contains PII like PAN, Aadhaar, Email, Phone, or Account numbers.
        """
        # PAN pattern: 5 letters, 4 digits, 1 letter
        pan_pattern = re.compile(r'\b[A-Za-z]{5}\d{4}[A-Za-z]\b')
        # Aadhaar pattern: 12 digits, optional spaces/hyphens
        aadhaar_pattern = re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b')
        # Email pattern
        email_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
        # Phone pattern: 10 digits, optional country code prefix
        phone_pattern = re.compile(r'\b(?:\+91|0)?[6-9]\d{9}\b')
        # General numeric account number pattern: 9 to 18 digits
        account_pattern = re.compile(r'\b\d{9,18}\b')

        if (pan_pattern.search(query) or 
            aadhaar_pattern.search(query) or 
            email_pattern.search(query) or 
            phone_pattern.search(query) or 
            account_pattern.search(query)):
            return True
        return False

    def answer_query(self, query):
        # 1. PII detection check
        if self.detect_pii(query):
            return {
                "answer": "For security and privacy reasons, I do not process or store queries containing personal details (such as PAN, Aadhaar, bank account numbers, email addresses, or phone numbers). Please rephrase your question without any personal information.",
                "footer": "Privacy Safeguard Active",
                "citations": []
            }

        # 2. Compliance classification check
        if self.is_advisory_query(query):
            return {
                "answer": self.generate_advisory_refusal(),
                "footer": f"Last updated from sources: {datetime.date.today().strftime('%d %b %Y')}",
                "citations": []
            }

        # 2. Retrieve context from RAG
        retrieved_chunks = self.rag.retrieve(query, top_k=3)
        if not retrieved_chunks:
            return {
                "answer": "I could not find any relevant information to answer your query.",
                "footer": f"Last updated from sources: {datetime.date.today().strftime('%d %b %Y')}",
                "citations": []
            }

        context_blocks = []
        citations = []
        last_updated = retrieved_chunks[0]["last_updated"] if retrieved_chunks else datetime.date.today().strftime('%d %b %Y')
        
        for chunk in retrieved_chunks:
            context_blocks.append(f"Source: {chunk['url']}\nContent:\n{chunk['content']}")
            if chunk["url"] not in citations:
                citations.append(chunk["url"])
                
        context_str = "\n\n---\n\n".join(context_blocks)
        primary_source = citations[0] if citations else "https://groww.in"

        if not self.client:
            # Offline fallback response if no client is configured
            best_chunk = retrieved_chunks[0]["content"]
            first_lines = best_chunk.split("\n")[:2]
            fallback_answer = " ".join(first_lines)
            return {
                "answer": self.validate_citation(self.clean_sentence_count(fallback_answer), primary_source),
                "footer": f"Last updated from sources: {last_updated}",
                "citations": citations
            }

        # 3. Prompt engineering with strict compliance constraints for Groq LLM
        system_prompt = (
            "You are a facts-only Mutual Fund FAQ Assistant for Motilal Oswal schemes. Your job is to answer queries strictly using the provided context.\n"
            "Constraints:\n"
            "- State only facts directly mentioned in the context. Do not speculate, extrapolate, or suggest anything.\n"
            "- Absolutely NO investment advice, opinions, or recommendations.\n"
            "- Limit the response to a maximum of 3 sentences.\n"
            f"- Include exactly one markdown hyperlink pointing to the source URL: {primary_source} (e.g., [Groww]({primary_source})).\n"
            "- If the context does not contain enough details to answer, state: 'I do not have the verified details to answer this query in the current corpus.' and include the source link.\n"
        )
        
        prompt = (
            f"Context:\n{context_str}\n\n"
            f"Query: \"{query}\"\n\n"
            "Factual Answer (max 3 sentences, 1 citation):"
        )

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=DEFAULT_MODEL,
                temperature=0.1
            )
            raw_answer = response.choices[0].message.content.strip()
            
            # Post-processing constraint verification
            cleaned_answer = self.clean_sentence_count(raw_answer, max_sentences=3)
            final_answer = self.validate_citation(cleaned_answer, primary_source)
            
            return {
                "answer": final_answer,
                "footer": f"Last updated from sources: {last_updated}",
                "citations": citations
            }
        except Exception as e:
            print(f"Error calling Groq: {e}. Trying fallback model...")
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=FALLBACK_MODEL,
                    temperature=0.1
                )
                raw_answer = response.choices[0].message.content.strip()
                cleaned_answer = self.clean_sentence_count(raw_answer, max_sentences=3)
                final_answer = self.validate_citation(cleaned_answer, primary_source)
                return {
                    "answer": final_answer,
                    "footer": f"Last updated from sources: {last_updated}",
                    "citations": citations
                }
            except Exception as e2:
                print(f"Error calling Groq fallback: {e2}")
                # Fallback to offline rule-based response
                return {
                    "answer": f"An error occurred while generating the answer. Please check the source directly: [Groww]({primary_source})",
                    "footer": f"Last updated from sources: {last_updated}",
                    "citations": citations
                }

if __name__ == "__main__":
    # Test query
    bot = FAQChatbot()
    print("\n--- Test Query (Factual via Groq) ---")
    res1 = bot.answer_query("What is the expense ratio of the Motilal Oswal Large and Midcap Fund?")
    print(f"Answer: {res1['answer']}")
    print(f"Footer: {res1['footer']}")
    
    print("\n--- Test Query (Advisory via Groq) ---")
    res2 = bot.answer_query("Should I invest in the Motilal Oswal Active Momentum Fund?")
    print(f"Answer: {res2['answer']}")
