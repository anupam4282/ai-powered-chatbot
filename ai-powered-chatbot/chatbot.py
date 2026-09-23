import re
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download small NLTK resources if they are not already available.
for resource, package in [
    ("tokenizers/punkt", "punkt"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
]:
    try:
        nltk.data.find(resource)
    except LookupError:
        nltk.download(package, quiet=True)

class Chatbot:
    """
    Hybrid chatbot:
    1. NLTK cleans and normalizes the user's message.
    2. FAQ intent matching handles common support questions reliably.
    3. A Transformer model is used for more open-ended responses when enabled.
    4. A safe fallback keeps the application usable if the model is unavailable.
    """

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))
        self.generator = None
        self.model_loaded = False

        self.faqs = {
            "greeting": {
                "keywords": {"hello", "hi", "hey", "greetings"},
                "response": "Hello! 👋 I'm your AI support assistant. How can I help you today?"
            },
            "thanks": {
                "keywords": {"thanks", "thank", "appreciate"},
                "response": "You're welcome! 😊 Is there anything else I can help you with?"
            },
            "hours": {
                "keywords": {"hour", "hours", "open", "closed", "timing", "time"},
                "response": "Our support team is available Monday to Friday, 9:00 AM to 6:00 PM."
            },
            "contact": {
                "keywords": {"contact", "email", "phone", "support"},
                "response": "You can contact support through the support email or phone number provided by your organization."
            },
            "refund": {
                "keywords": {"refund", "money", "return", "reimbursement"},
                "response": "Refund requests are normally reviewed within 3–5 business days. Please keep your order or transaction ID ready."
            },
            "password": {
                "keywords": {"password", "forgot", "reset", "login", "signin"},
                "response": "If you forgot your password, use the 'Forgot Password' option on the login page and follow the reset instructions."
            },
            "order": {
                "keywords": {"order", "delivery", "shipment", "track", "tracking"},
                "response": "For order tracking, please provide your order ID. You can also check the tracking section of your account."
            },
            "features": {
                "keywords": {"feature", "features", "help", "capability", "can"},
                "response": "I can answer FAQs, help with common support questions, maintain conversation history, and generate contextual responses."
            },
            "goodbye": {
                "keywords": {"bye", "goodbye", "exit", "quit"},
                "response": "Goodbye! 👋 Have a great day!"
            },
        }

    def preprocess(self, text):
        text = text.lower()
        tokens = re.findall(r"[a-zA-Z']+", text)
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        return tokens

    def faq_response(self, message):
        tokens = set(self.preprocess(message))
        if not tokens:
            return None

        best_name = None
        best_score = 0

        for name, item in self.faqs.items():
            score = len(tokens.intersection(item["keywords"]))
            if score > best_score:
                best_score = score
                best_name = name

        # Require at least one useful keyword.
        if best_name and best_score >= 1:
            return self.faqs[best_name]["response"]
        return None

    @lru_cache(maxsize=1)
    def load_transformer(self):
        try:
            from transformers import pipeline
            self.generator = pipeline(
                "text-generation",
                model="distilgpt2",
                device=-1
            )
            self.model_loaded = True
            return True
        except Exception as exc:
            print(f"Transformer model unavailable: {exc}")
            self.model_loaded = False
            return False

    def transformer_response(self, message):
        if not self.load_transformer():
            return None

        prompt = (
            "You are a helpful customer support chatbot. "
            "Give a short, polite, useful answer.\n"
            f"User: {message}\nAssistant:"
        )

        try:
            result = self.generator(
                prompt,
                max_new_tokens=60,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                num_return_sequences=1,
            )
            generated = result[0]["generated_text"]
            answer = generated.split("Assistant:", 1)[-1].strip()
            answer = answer.split("User:", 1)[0].strip()
            if answer:
                return answer
        except Exception as exc:
            print(f"Transformer generation failed: {exc}")
        return None

    def reply(self, message):
        faq = self.faq_response(message)
        if faq:
            return faq

        ai_response = self.transformer_response(message)
        if ai_response:
            return ai_response

        return (
            "I'm not completely sure about that yet. "
            "Could you rephrase your question or ask about orders, refunds, "
            "passwords, support hours, or available features?"
        )
