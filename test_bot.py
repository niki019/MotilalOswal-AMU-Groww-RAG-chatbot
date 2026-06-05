import re
import unittest
from chatbot import FAQChatbot

class TestFAQChatbotCompliance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Initializing FAQChatbot for compliance testing...")
        cls.bot = FAQChatbot()

    def count_sentences(self, text):
        pattern = r'(?<!\b[Mm]r\.)(?<!\b[Mm]rs\.)(?<!\b[Dd]r\.)(?<!\b[Mm]s\.)(?<!\b[Ll]td\.)(?<!\b[Cc]o\.)(?<!\b[Cc]r\.)(?<!\b[Ee]\.[Gg]\.)(?<!\b[Ii]\.[Ee]\.)(?<=[.!?])\s+'
        return len([s for s in re.split(pattern, text.strip()) if s])

    def test_advisory_query_refusal_1(self):
        query = "Should I invest in the Motilal Oswal Active Momentum Fund?"
        print(f"\nTesting advisory query: '{query}'")
        res = self.bot.answer_query(query)
        answer = res["answer"]
        print(f"Response: {answer}")
        
        # Must refuse and refer to AMFI or SEBI
        self.assertTrue(
            "cannot provide investment advice" in answer.lower() or 
            "facts-only" in answer.lower(),
            "Advisory query did not return a proper refusal message."
        )
        self.assertTrue(
            "amfiindia.com" in answer or "sebi.gov.in" in answer,
            "Refusal message did not contain AMFI/SEBI educational resource links."
        )
        self.assertIn("citations", res)

    def test_advisory_query_refusal_2(self):
        query = "Which Motilal Oswal fund is better for retirement: Contra or Digital India?"
        print(f"\nTesting advisory query: '{query}'")
        res = self.bot.answer_query(query)
        answer = res["answer"]
        print(f"Response: {answer}")
        
        self.assertTrue(
            "cannot provide" in answer.lower() or "refuse" in answer.lower() or "facts-only" in answer.lower(),
            "Advisory query did not return a proper refusal message."
        )
        self.assertTrue(
            "amfiindia.com" in answer or "sebi.gov.in" in answer,
            "Refusal message did not contain AMFI/SEBI educational resource links."
        )

    def test_factual_query_expense_ratio(self):
        query = "What is the expense ratio of the Motilal Oswal Large and Midcap Fund?"
        print(f"\nTesting factual query: '{query}'")
        res = self.bot.answer_query(query)
        answer = res["answer"]
        footer = res["footer"]
        print(f"Response: {answer}")
        print(f"Footer: {footer}")
        
        # 1. Check sentence count (<= 3 sentences)
        sentence_count = self.count_sentences(answer)
        self.assertLessEqual(sentence_count, 3, f"Response has {sentence_count} sentences, exceeds limit of 3.")
        
        # 2. Check exactly one markdown hyperlink
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', answer)
        self.assertEqual(len(links), 1, f"Expected exactly 1 markdown link, found {len(links)}: {links}")
        
        # 3. Verify it contains the correct expense ratio (0.73%)
        self.assertIn("0.73%", answer, "Response does not mention correct expense ratio of 0.73%.")
        
        # 4. Verify footer exists and contains updated date
        self.assertTrue("Last updated from sources" in footer, "Footer is missing last updated info.")

    def test_factual_query_managers(self):
        query = "Who are the fund managers of Motilal Oswal Digital India Fund?"
        print(f"\nTesting factual query: '{query}'")
        res = self.bot.answer_query(query)
        answer = res["answer"]
        print(f"Response: {answer}")
        
        # 1. Check sentence count (<= 3 sentences)
        sentence_count = self.count_sentences(answer)
        self.assertLessEqual(sentence_count, 3, f"Response has {sentence_count} sentences, exceeds limit of 3.")
        
        # 2. Check exactly one markdown hyperlink
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', answer)
        self.assertEqual(len(links), 1, f"Expected exactly 1 markdown link, found {len(links)}: {links}")
        
        # 3. Check that it mentions Mr. Mayekar (from managers details)
        self.assertTrue("Mayekar" in answer, "Response does not name the fund manager(s).")

    def test_factual_query_exit_load(self):
        query = "What is the exit load of Motilal Oswal Contra Fund?"
        print(f"\nTesting factual query: '{query}'")
        res = self.bot.answer_query(query)
        answer = res["answer"]
        print(f"Response: {answer}")
        
        # 1. Check sentence count (<= 3 sentences)
        sentence_count = self.count_sentences(answer)
        self.assertLessEqual(sentence_count, 3, f"Response has {sentence_count} sentences, exceeds limit of 3.")
        
        # 2. Check exactly one markdown hyperlink
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', answer)
        self.assertEqual(len(links), 1, f"Expected exactly 1 markdown link, found {len(links)}: {links}")
        
        # 3. Verify it contains the exit load info (1% if redeemed within 15 days)
        self.assertTrue("1%" in answer or "15 days" in answer or "15-days" in answer, "Response does not mention exit load details properly.")

    def test_pii_refusal(self):
        pii_queries = [
            "My PAN is ABCDE1234F, what is my tax?",
            "Can you help me with Aadhaar 1234-5678-9012?",
            "Call me at +919876543210 to explain exit load",
            "Send info to user@test.com",
            "Check my account 123456789012"
        ]
        for query in pii_queries:
            print(f"\nTesting PII query: '{query}'")
            res = self.bot.answer_query(query)
            answer = res["answer"]
            print(f"Response: {answer}")
            self.assertTrue(
                "privacy" in answer.lower() or "personal" in answer.lower() or "security" in answer.lower(),
                f"PII query '{query}' did not trigger a privacy refusal."
            )

if __name__ == "__main__":
    unittest.main()
