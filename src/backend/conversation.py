# ChillBuddy Mental Health Chatbot - Conversation Engine
# This file handles the core conversation logic and AI model integration
# Author: ChillBuddy Team
# Date: 2025

import json
import logging
import os
import torch
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline,
    GPT2LMHeadModel,
    GPT2Tokenizer
)
from pathlib import Path

class ConversationEngine:
    """
    Core conversation engine for ChillBuddy mental health chatbot.
    Handles AI model loading, response generation, and conversation management.
    """
    
    def __init__(self, model_config_path: str = "models/model_config.json"):
        """
        Initialize the conversation engine with model configuration.
        
        Args:
            model_config_path (str): Path to model configuration file
        """
        self.model_config_path = model_config_path
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.fallback_model = None
        self.fallback_tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Configuration and data storage
        self.config = {}
        self.conversation_history = {}
        self.fallback_responses = {}
        self.conversation_templates = {}
        self.safety_filters = {}
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Initialize components
        try:
            self._load_config()
            self._load_templates()
            self._initialize_model()
            self.logger.info("ConversationEngine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ConversationEngine: {e}")
            self._initialize_fallback_only()
    
    def _load_config(self) -> None:
        """
        Load model configuration from JSON file.
        """
        try:
            config_path = Path(self.model_config_path)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info("Model configuration loaded successfully")
            else:
                self.logger.warning(f"Config file not found: {config_path}")
                self._load_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """
        Load default configuration when config file is not available.
        """
        self.config = {
            "primary_model": {
                "name": "microsoft/DialoGPT-medium",
                "type": "causal_lm",
                "load_method": "online"
            },
            "fallback_model": {
                "name": "microsoft/DialoGPT-small",
                "type": "causal_lm"
            },
            "generation_params": {
                "max_length": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "pad_token_id": 50256
            },
            "safety_settings": {
                "enable_content_filter": True,
                "enable_crisis_detection": True
            }
        }
        self.logger.info("Default configuration loaded")
    
    def _initialize_model(self) -> None:
        """
        Initialize the AI model and tokenizer.
        Supports both online and offline model loading.
        """
        try:
            # Get model name from correct config structure
            model_settings = self.config.get("model_settings", {})
            primary_model = model_settings.get("primary_model", {})
            model_name = primary_model.get("name", "microsoft/DialoGPT-medium")
            
            self.logger.info(f"Loading primary model: {model_name}")
            
            # Check model type from config
            model_type = primary_model.get("type", "causal_lm")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                padding_side='left'
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model based on type
            if model_type == "seq2seq":
                from transformers import AutoModelForSeq2SeqLM
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                self.model_type = "seq2seq"
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                self.model_type = "causal_lm"
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            # Create pipeline based on model type
            if hasattr(self, 'model_type') and self.model_type == "seq2seq":
                self.pipeline = pipeline(
                    "text2text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == "cuda" else -1
                )
            else:
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == "cuda" else -1
                )
            
            self.logger.info(f"Model loaded successfully on {self.device}")
            
            # Load fallback model
            self._load_fallback_model()
            
        except Exception as e:
            self.logger.error(f"Error loading primary model: {e}")
            self._initialize_fallback_only()
    
    def _load_fallback_model(self) -> None:
        """
        Load a smaller fallback model for emergency situations.
        """
        try:
            # Get fallback model name from correct config structure
            model_settings = self.config.get("model_settings", {})
            fallback_model = model_settings.get("fallback_model", {})
            fallback_name = fallback_model.get("name", "microsoft/DialoGPT-small")
            
            self.logger.info(f"Loading fallback model: {fallback_name}")
            
            self.fallback_tokenizer = GPT2Tokenizer.from_pretrained(fallback_name)
            self.fallback_model = GPT2LMHeadModel.from_pretrained(fallback_name)
            
            if self.fallback_tokenizer.pad_token is None:
                self.fallback_tokenizer.pad_token = self.fallback_tokenizer.eos_token
            
            self.fallback_model = self.fallback_model.to(self.device)
            
            self.logger.info("Fallback model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading fallback model: {e}")
    
    def _initialize_fallback_only(self) -> None:
        """
        Initialize with fallback responses only when models fail to load.
        """
        self.logger.warning("Initializing with fallback responses only")
        self.model = None
        self.tokenizer = None
        self.pipeline = None
    
    def _load_templates(self) -> None:
        """
        Load conversation templates and fallback responses.
        """
        # Load fallback responses
        try:
            fallback_path = Path("models/fallback_responses.json")
            if fallback_path.exists():
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    self.fallback_responses = json.load(f)
                self.logger.info("Fallback responses loaded")
            else:
                self._load_default_fallback_responses()
        except Exception as e:
            self.logger.error(f"Error loading fallback responses: {e}")
            self._load_default_fallback_responses()
        
        # Load conversation templates
        try:
            templates_path = Path("models/conversation_templates.json")
            if templates_path.exists():
                with open(templates_path, 'r', encoding='utf-8') as f:
                    self.conversation_templates = json.load(f)
                self.logger.info("Conversation templates loaded")
        except Exception as e:
            self.logger.error(f"Error loading conversation templates: {e}")
        
        # Load safety filters
        try:
            safety_path = Path("models/safety_filters.json")
            if safety_path.exists():
                with open(safety_path, 'r', encoding='utf-8') as f:
                    self.safety_filters = json.load(f)
                self.logger.info("Safety filters loaded")
        except Exception as e:
            self.logger.error(f"Error loading safety filters: {e}")
    
    def _load_default_fallback_responses(self) -> None:
        """
        Load default fallback responses when file is not available.
        """
        self.fallback_responses = {
            "general_support": [
                "I'm here to listen and support you. How are you feeling today?",
                "Thank you for sharing with me. What's on your mind?",
                "I understand this might be difficult. Would you like to talk about it?"
            ],
            "crisis_response": [
                "I'm concerned about what you're going through. Please consider reaching out to a mental health professional or crisis helpline.",
                "Your safety is important. If you're in immediate danger, please contact emergency services or a crisis helpline."
            ],
            "technical_error": [
                "I'm experiencing some technical difficulties. Let me try to help you in a different way.",
                "I apologize for the technical issue. How can I best support you right now?"
            ]
        }

    def generate_response(self, user_message: str, user_id: str = None, context: Dict = None) -> Dict[str, Any]:
        """
        Generate a response to user input with safety checks and context awareness.
        
        Args:
            user_message (str): The user's input message
            user_id (str): Unique identifier for the user
            context (Dict): Additional context for the conversation
            
        Returns:
            Dict: Response containing message, confidence, safety_flags, etc.
        """
        try:
            # Preprocess input
            cleaned_message = self._preprocess_input(user_message)
            
            # Safety check
            safety_result = self._check_safety(cleaned_message)
            if safety_result.get("is_crisis"):
                return self._handle_crisis_response(safety_result)
            
            # Generate response
            if self.pipeline:
                response = self._generate_ai_response(cleaned_message, context)
            else:
                response = self._get_fallback_response("technical_error")
            
            # Post-process response
            final_response = self._postprocess_response(response, user_message)
            
            # Update conversation history
            if user_id:
                self._update_conversation_history(user_id, user_message, final_response)
            
            return {
                "message": final_response,
                "confidence": 0.8,
                "safety_flags": safety_result if isinstance(safety_result, dict) else {
                    "risk_level": getattr(safety_result, 'risk_level', 'low'),
                    "detected_keywords": getattr(safety_result, 'detected_keywords', []),
                    "confidence_score": getattr(safety_result, 'confidence_score', 0.0)
                },
                "timestamp": datetime.now().isoformat(),
                "source": "ai" if self.pipeline else "fallback"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                "message": self._get_fallback_response("technical_error"),
                "confidence": 0.3,
                "safety_flags": {"error": True},
                "timestamp": datetime.now().isoformat(),
                "source": "fallback"
            }
    
    def _preprocess_input(self, message: str) -> str:
        """
        Clean and prepare user input for processing.
        
        Args:
            message (str): Raw user input
            
        Returns:
            str: Cleaned message
        """
        if not message:
            return ""
        
        # Basic cleaning
        cleaned = message.strip()
        
        # Remove excessive whitespace
        cleaned = " ".join(cleaned.split())
        
        # Limit length
        max_length = 500
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def _check_safety(self, message: str) -> Dict[str, Any]:
        """
        Check message for safety concerns and crisis indicators.
        
        Args:
            message (str): User message to check
            
        Returns:
            Dict: Safety analysis results
        """
        safety_result = {
            "is_crisis": False,
            "crisis_type": None,
            "confidence": 0.0,
            "keywords_detected": []
        }
        
        if not message:
            return safety_result
        
        message_lower = message.lower()
        
        # Crisis keywords from safety filters
        crisis_keywords = list(self.safety_filters.get("crisis_detection", {}).get("suicide_keywords", []))
        self_harm_keywords = self.safety_filters.get("crisis_detection", {}).get("self_harm_keywords", [])
        if isinstance(self_harm_keywords, list):
            crisis_keywords.extend(self_harm_keywords)
        
        # Default crisis keywords if filters not loaded
        if not crisis_keywords:
            crisis_keywords = [
                "suicide", "kill myself", "end my life", "want to die", 
                "hurt myself", "self harm", "cutting", "overdose",
                "hopeless", "can't go on", "better off dead"
            ]
        
        detected_keywords = []
        for keyword in crisis_keywords:
            if keyword.lower() in message_lower:
                detected_keywords.append(keyword)
        
        if detected_keywords:
            safety_result.update({
                "is_crisis": True,
                "crisis_type": "self_harm" if any(word in ["hurt", "harm", "cut"] for word in detected_keywords) else "suicide",
                "confidence": min(0.9, len(detected_keywords) * 0.3),
                "keywords_detected": detected_keywords
            })
        
        return safety_result
    
    def _generate_ai_response(self, message: str, context: Dict = None) -> str:
        """
        Generate response using the AI model.
        
        Args:
            message (str): Preprocessed user message
            context (Dict): Conversation context
            
        Returns:
            str: Generated response
        """
        try:
            # Prepare prompt with context
            prompt = self._prepare_prompt(message, context)
            
            # Generation parameters
            gen_params = self.config.get("generation_parameters", {})
            
            # Generate response
            outputs = self.pipeline(
                prompt,
                max_new_tokens=gen_params.get("max_new_tokens", 100),
                temperature=gen_params.get("temperature", 0.7),
                top_p=gen_params.get("top_p", 0.9),
                do_sample=gen_params.get("do_sample", True),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                truncation=True,
                num_return_sequences=1
            )
            
            # Extract response based on model type
            if hasattr(self, 'model_type') and self.model_type == "seq2seq":
                # For seq2seq models, the output is the direct response
                response = outputs[0]['generated_text'].strip()
            else:
                # For causal LM, extract the new part after the prompt
                generated_text = outputs[0]['generated_text']
                response = generated_text[len(prompt):].strip()
            
            # Clean up response - remove incomplete sentences
            if response:
                # Split by sentences and take complete ones
                sentences = response.split('.')
                if len(sentences) > 1:
                    # Keep all complete sentences except the last incomplete one
                    complete_sentences = sentences[:-1]
                    if complete_sentences:
                        response = '. '.join(complete_sentences) + '.'
            
            # Fallback to template only if response is extremely short or empty
            if len(response) < 5:
                return self._get_template_response("general_support")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in AI generation: {e}")
            return self._get_fallback_response("technical_error")
    
    def _prepare_prompt(self, message: str, context: Dict = None) -> str:
        """
        Prepare the prompt for the AI model with context and formatting.
        
        Args:
            message (str): User message
            context (Dict): Conversation context
            
        Returns:
            str: Formatted prompt
        """
        # Format prompt based on model type
        if hasattr(self, 'model_type') and self.model_type == "seq2seq":
            # For seq2seq models like GODEL, use minimal prompting to avoid identity confusion
            # Simply provide the user message with minimal context
            if context and context.get("history"):
                # Include only the most recent exchange for continuity
                history = context["history"][-1:]  # Last exchange only
                context_str = ""
                for exchange in history:
                    if exchange.get('user'):
                        context_str += f"{exchange['user']} "
                
                if context_str:
                    prompt = f"{context_str.strip()} {message}"
                else:
                    prompt = message
            else:
                prompt = message
        else:
            # For causal LM models like DialoGPT, use conversation format
            conversation_history = ""
            
            # Add conversation history if available
            if context and context.get("history"):
                history = context["history"][-2:]  # Last 2 exchanges to keep context manageable
                for exchange in history:
                    if exchange.get('user') and exchange.get('bot'):
                        conversation_history += f"Human: {exchange['user']}\n"
                        conversation_history += f"Bot: {exchange['bot']}\n"
            
            # Create the prompt with proper formatting for DialoGPT
            if conversation_history:
                prompt = f"{conversation_history}Human: {message}\nBot:"
            else:
                # For first message, provide some context
                prompt = f"Human: {message}\nBot:"
        
        return prompt
    
    def _postprocess_response(self, response: str, original_message: str) -> str:
        """
        Post-process the generated response for quality and safety.
        
        Args:
            response (str): Raw generated response
            original_message (str): Original user message
            
        Returns:
            str: Processed response
        """
        if not response:
            return self._get_fallback_response("general_support")
        
        # Clean up response
        response = response.strip()
        
        # Remove any repetitive patterns
        lines = response.split('\n')
        unique_lines = []
        for line in lines:
            if line.strip() and line.strip() not in unique_lines:
                unique_lines.append(line.strip())
        
        response = ' '.join(unique_lines)
        
        # Aggressive repetition removal - handle multiple patterns
        import re
        
        # Remove obvious sentence repetitions (like "I'm sorry. I'm sorry.")
        sentences = re.split(r'[.!?]+', response)
        unique_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in unique_sentences:
                unique_sentences.append(sentence)
        response = '. '.join(unique_sentences)
        if response and not response.endswith(('.', '!', '?')):
            response += '.'
        
        # Ultra-aggressive repetition removal
        # First, handle phrase-level repetitions within sentences
        def remove_phrase_repetitions(text):
            # Split by common delimiters
            parts = re.split(r'[,;]', text)
            unique_parts = []
            
            for part in parts:
                part = part.strip()
                if part:
                    # Check if this part (or very similar) already exists
                    is_duplicate = False
                    for existing in unique_parts:
                        # Check for exact match or very high similarity
                        if part.lower() == existing.lower():
                            is_duplicate = True
                            break
                        # Check for substantial overlap (>70% of words)
                        part_words = set(part.lower().split())
                        existing_words = set(existing.lower().split())
                        if len(part_words) > 0 and len(existing_words) > 0:
                            overlap = len(part_words.intersection(existing_words))
                            similarity = overlap / max(len(part_words), len(existing_words))
                            if similarity > 0.7:
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        unique_parts.append(part)
            
            return ', '.join(unique_parts)
        
        response = remove_phrase_repetitions(response)
        
        # Then handle word-level repetition
        words = response.split()
        if len(words) > 1:
            cleaned_words = []
            i = 0
            
            while i < len(words):
                current_word = words[i]
                
                # Skip if this exact word sequence already appeared recently
                skip_word = False
                if len(cleaned_words) >= 3:
                    # Check if current word starts a sequence we've seen before
                    for lookback in range(1, min(6, len(cleaned_words) + 1)):
                        if i + lookback <= len(words):
                            current_seq = words[i:i + lookback]
                            recent_seq = cleaned_words[-lookback:]
                            if [w.lower() for w in current_seq] == [w.lower() for w in recent_seq]:
                                skip_word = True
                                i += lookback - 1  # Skip the entire sequence
                                break
                
                if not skip_word:
                    cleaned_words.append(current_word)
                
                i += 1
            
            response = ' '.join(cleaned_words)
        
        # Ensure response is not too long
        max_response_length = 300
        if len(response) > max_response_length:
            response = response[:max_response_length].rsplit(' ', 1)[0] + "..."
        
        # Only add empathetic elements for very short, clinical responses
        if len(response) < 20 and not any(word in response.lower() for word in ['feel', 'understand', 'here', 'support', 'hello', 'hi']):
            empathy_prefix = "I understand. "
            response = empathy_prefix + response
        
        return response
    
    def _handle_crisis_response(self, safety_result: Dict) -> Dict[str, Any]:
        """
        Handle crisis situations with appropriate responses and resources.
        
        Args:
            safety_result (Dict): Safety analysis results
            
        Returns:
            Dict: Crisis response
        """
        crisis_responses = self.fallback_responses.get("crisis_response", [
            "I'm very concerned about what you're going through. Please reach out to a mental health professional immediately.",
            "Your safety is the most important thing right now. Please contact a crisis helpline or emergency services."
        ])
        
        # Add South African crisis resources
        sa_resources = (
            "\n\nSouth African Crisis Resources:\n"
            "• SADAG Crisis Line: 0800 567 567\n"
            "• Lifeline: 0861 322 322\n"
            "• Emergency Services: 10111\n"
            "• SMS Crisis Line: 31393"
        )
        
        response_message = crisis_responses[0] + sa_resources
        
        return {
            "message": response_message,
            "confidence": 1.0,
            "safety_flags": safety_result,
            "timestamp": datetime.now().isoformat(),
            "source": "crisis_protocol",
            "requires_escalation": True
        }
    
    def _get_fallback_response(self, category: str = "general_support") -> str:
        """
        Get a fallback response from predefined templates.
        
        Args:
            category (str): Category of fallback response
            
        Returns:
            str: Fallback response
        """
        import random
        
        # Map categories to appropriate fallback responses
        if category == "technical_error":
            responses = self.fallback_responses.get("system_errors", {}).get("response_generation_failed", [])
        elif category == "general_support":
            responses = self.fallback_responses.get("conversation_starters", {}).get("general_greeting", [])
        else:
            responses = self.fallback_responses.get(category, [])
        
        # Default fallback if no responses found
        if not responses:
            responses = [
                "I'm here to support you. How are you feeling today?",
                "I want to help you through whatever you're experiencing. Can you tell me more?",
                "Your wellbeing is important to me. What's on your mind?"
            ]
        
        return random.choice(responses)
    
    def _get_template_response(self, template_type: str) -> str:
        """
        Get a response from conversation templates.
        
        Args:
            template_type (str): Type of template response
            
        Returns:
            str: Template response
        """
        import random
        
        # Map template types to appropriate responses
        if template_type == "general_support":
            # Use greeting templates for general support
            templates = self.conversation_templates.get("greeting_templates", {})
            first_visit = templates.get("first_visit", {})
            message = first_visit.get("message", "")
            if message:
                return message
        elif template_type == "mood_check":
            templates = self.conversation_templates.get("mood_check_templates", {})
            initial = templates.get("initial_assessment", {})
            prompts = initial.get("prompts", [])
            if prompts:
                return random.choice(prompts)
        
        # Fallback to general support responses
        return self._get_fallback_response("general_support")
    
    def _update_conversation_history(self, user_id: str, user_message: str, bot_response: str) -> None:
        """
        Update conversation history for the user.
        
        Args:
            user_id (str): User identifier
            user_message (str): User's message
            bot_response (str): Bot's response
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "bot": bot_response
        })
        
        # Keep only last 50 exchanges per user
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """
        Get conversation history for a user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            List[Dict]: Conversation history
        """
        return self.conversation_history.get(user_id, [])
    
    def clear_conversation_history(self, user_id: str) -> None:
        """
        Clear conversation history for a user.
        
        Args:
            user_id (str): User identifier
        """
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
    
    def is_model_loaded(self) -> bool:
        """
        Check if the AI model is successfully loaded.
        
        Returns:
            bool: True if model is loaded, False otherwise
        """
        return self.model is not None and self.tokenizer is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dict: Model information
        """
        return {
            "model_loaded": self.is_model_loaded(),
            "device": self.device,
            "model_name": self.config.get("primary_model", {}).get("name", "Unknown"),
            "fallback_available": self.fallback_model is not None,
            "templates_loaded": len(self.conversation_templates) > 0,
            "safety_filters_loaded": len(self.safety_filters) > 0
        }

# Helper Functions for external use
def clean_text(text: str) -> str:
    """
    Clean and normalize text input.
    
    Args:
        text (str): Raw text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = " ".join(text.strip().split())
    return cleaned

def detect_crisis_keywords(text: str, keywords: List[str] = None) -> List[str]:
    """
    Detect crisis-related keywords in text.
    
    Args:
        text (str): Text to analyze
        keywords (List[str]): Custom keywords to check
        
    Returns:
        List[str]: Detected crisis keywords
    """
    if not text:
        return []
    
    if keywords is None:
        keywords = [
            "suicide", "kill myself", "end my life", "want to die",
            "hurt myself", "self harm", "cutting", "overdose"
        ]
    
    text_lower = text.lower()
    detected = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            detected.append(keyword)
    
    return detected

if __name__ == "__main__":
    # Test the conversation engine
    engine = ConversationEngine()
    print(f"Model info: {engine.get_model_info()}")
    
    # Test response generation
    test_response = engine.generate_response("Hello, I'm feeling a bit anxious today.")
    print(f"Test response: {test_response}")