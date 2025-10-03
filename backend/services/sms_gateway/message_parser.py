"""Message parsing and validation for SMS messages."""
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MessageIntent(str, Enum):
    """Detected message intents."""
    GREETING = "greeting"
    QUESTION = "question"
    EMERGENCY = "emergency"
    COMMAND = "command"
    INFORMATION = "information"
    UNKNOWN = "unknown"


class MessageCategory(str, Enum):
    """Message categories for routing."""
    GENERAL = "general"
    EMERGENCY = "emergency"
    WEATHER = "weather"
    NEWS = "news"
    EDUCATION = "education"
    HEALTH = "health"
    TRANSPORT = "transport"
    GOVERNMENT = "government"


@dataclass
class ParsedMessage:
    """Parsed message with extracted information."""
    original_text: str
    intent: MessageIntent
    category: MessageCategory
    entities: Dict[str, Any]
    confidence: float
    requires_rag: bool
    requires_llm: bool
    priority: str
    language: str
    clean_text: str


class MessageParser:
    """SMS message parser and validator."""
    
    def __init__(self):
        # Emergency keywords
        self.emergency_keywords = [
            'emergency', 'help', 'urgent', 'fire', 'police', 'ambulance',
            'accident', 'danger', 'crisis', 'disaster', 'flood', 'earthquake',
            'hurricane', 'tornado', 'bomb', 'attack', 'violence', 'theft',
            'robbery', 'assault', 'rape', 'murder', 'suicide', 'overdose',
            'heart attack', 'stroke', 'unconscious', 'bleeding', 'injured'
        ]
        
        # Question patterns
        self.question_patterns = [
            r'\?', r'what', r'how', r'when', r'where', r'why', r'who',
            r'which', r'can you', r'could you', r'would you', r'do you know',
            r'tell me', r'explain', r'describe'
        ]
        
        # Command patterns
        self.command_patterns = [
            r'send', r'get', r'find', r'search', r'show', r'list',
            r'give me', r'provide', r'deliver', r'fetch'
        ]
        
        # Greeting patterns
        self.greeting_patterns = [
            r'hello', r'hi', r'hey', r'good morning', r'good afternoon',
            r'good evening', r'greetings', r'dear', r'sir', r'madam'
        ]
        
        # Category keywords
        self.category_keywords = {
            MessageCategory.WEATHER: ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'storm', 'forecast'],
            MessageCategory.NEWS: ['news', 'update', 'latest', 'happening', 'event', 'story'],
            MessageCategory.EDUCATION: ['learn', 'teach', 'school', 'education', 'study', 'course', 'lesson'],
            MessageCategory.HEALTH: ['health', 'doctor', 'hospital', 'medicine', 'sick', 'illness', 'treatment'],
            MessageCategory.TRANSPORT: ['bus', 'train', 'flight', 'transport', 'travel', 'route', 'schedule'],
            MessageCategory.GOVERNMENT: ['government', 'official', 'service', 'permit', 'license', 'document']
        }
        
        # Phone number patterns
        self.phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  # US format
            r'\+?[1-9]\d{1,14}',  # International format
        ]
        
        # Email patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # URL patterns
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
        # Profanity filter (basic)
        self.profanity_words = [
            # Add profanity words here for filtering
        ]
    
    def parse_message(self, message_text: str, sender: str = "") -> ParsedMessage:
        """Parse and validate SMS message."""
        try:
            # Clean and normalize text
            clean_text = self._clean_text(message_text)
            
            # Detect language (basic detection)
            language = self._detect_language(clean_text)
            
            # Detect intent
            intent, intent_confidence = self._detect_intent(clean_text)
            
            # Detect category
            category = self._detect_category(clean_text)
            
            # Extract entities
            entities = self._extract_entities(clean_text, sender)
            
            # Determine processing requirements
            requires_rag = self._requires_rag(clean_text, category)
            requires_llm = self._requires_llm(clean_text, intent)
            
            # Determine priority
            priority = self._determine_priority(intent, category, entities)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(intent_confidence, entities)
            
            return ParsedMessage(
                original_text=message_text,
                intent=intent,
                category=category,
                entities=entities,
                confidence=confidence,
                requires_rag=requires_rag,
                requires_llm=requires_llm,
                priority=priority,
                language=language,
                clean_text=clean_text
            )
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return ParsedMessage(
                original_text=message_text,
                intent=MessageIntent.UNKNOWN,
                category=MessageCategory.GENERAL,
                entities={},
                confidence=0.0,
                requires_rag=False,
                requires_llm=True,
                priority="normal",
                language="en",
                clean_text=message_text
            )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize message text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\?\.\,\!\@\#\$\%\^\&\*\(\)\+\=\-\_\|\~`\[\]\{\}\:\;\"\'\<\>\/\\]', '', text)
        
        # Convert to lowercase for processing
        return text.lower()
    
    def _detect_language(self, text: str) -> str:
        """Basic language detection."""
        # Simple heuristic - can be enhanced with proper language detection
        if any(word in text for word in ['hola', 'gracias', 'por favor', 'español']):
            return 'es'
        elif any(word in text for word in ['bonjour', 'merci', 'français']):
            return 'fr'
        else:
            return 'en'  # Default to English
    
    def _detect_intent(self, text: str) -> Tuple[MessageIntent, float]:
        """Detect message intent with confidence score."""
        text_lower = text.lower()
        
        # Check for emergency keywords
        emergency_matches = sum(1 for keyword in self.emergency_keywords if keyword in text_lower)
        if emergency_matches > 0:
            confidence = min(0.9, 0.5 + (emergency_matches * 0.1))
            return MessageIntent.EMERGENCY, confidence
        
        # Check for greeting patterns
        greeting_matches = sum(1 for pattern in self.greeting_patterns if re.search(pattern, text_lower))
        if greeting_matches > 0:
            confidence = min(0.8, 0.3 + (greeting_matches * 0.2))
            return MessageIntent.GREETING, confidence
        
        # Check for question patterns
        question_matches = sum(1 for pattern in self.question_patterns if re.search(pattern, text_lower))
        if question_matches > 0:
            confidence = min(0.8, 0.4 + (question_matches * 0.15))
            return MessageIntent.QUESTION, confidence
        
        # Check for command patterns
        command_matches = sum(1 for pattern in self.command_patterns if re.search(pattern, text_lower))
        if command_matches > 0:
            confidence = min(0.7, 0.3 + (command_matches * 0.2))
            return MessageIntent.COMMAND, confidence
        
        # Check for information keywords
        info_keywords = ['information', 'info', 'details', 'about', 'tell', 'explain']
        info_matches = sum(1 for keyword in info_keywords if keyword in text_lower)
        if info_matches > 0:
            confidence = min(0.6, 0.3 + (info_matches * 0.15))
            return MessageIntent.INFORMATION, confidence
        
        return MessageIntent.UNKNOWN, 0.1
    
    def _detect_category(self, text: str) -> MessageCategory:
        """Detect message category."""
        text_lower = text.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return MessageCategory.GENERAL
    
    def _extract_entities(self, text: str, sender: str) -> Dict[str, Any]:
        """Extract entities from message text."""
        entities = {
            'phone_numbers': [],
            'emails': [],
            'urls': [],
            'numbers': [],
            'locations': [],
            'dates': [],
            'keywords': []
        }
        
        # Extract phone numbers
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            entities['phone_numbers'].extend(matches)
        
        # Extract emails
        email_matches = re.findall(self.email_pattern, text)
        entities['emails'].extend(email_matches)
        
        # Extract URLs
        url_matches = re.findall(self.url_pattern, text)
        entities['urls'].extend(url_matches)
        
        # Extract numbers
        number_matches = re.findall(r'\b\d+\b', text)
        entities['numbers'].extend(number_matches)
        
        # Extract locations (basic pattern matching)
        location_patterns = [
            r'\b[A-Z][a-z]+ (?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b',
            r'\b[A-Z][a-z]+, [A-Z]{2}\b',  # City, State
        ]
        for pattern in location_patterns:
            location_matches = re.findall(pattern, text)
            entities['locations'].extend(location_matches)
        
        # Extract dates (basic patterns)
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        for pattern in date_patterns:
            date_matches = re.findall(pattern, text)
            entities['dates'].extend(date_matches)
        
        # Extract important keywords
        important_words = []
        words = text.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                # Check if word appears in any of our keyword lists
                word_lower = word.lower()
                if (word_lower in self.emergency_keywords or 
                    any(word_lower in keywords for keywords in self.category_keywords.values()) or
                    any(word_lower in pattern for pattern in self.question_patterns)):
                    important_words.append(word)
        
        entities['keywords'] = important_words
        
        # Add sender information
        entities['sender'] = sender
        
        return entities
    
    def _requires_rag(self, text: str, category: MessageCategory) -> bool:
        """Determine if message requires RAG processing."""
        # Emergency messages don't need RAG
        if category == MessageCategory.EMERGENCY:
            return False
        
        # Information requests likely need RAG
        if category in [MessageCategory.WEATHER, MessageCategory.NEWS, MessageCategory.EDUCATION, 
                       MessageCategory.HEALTH, MessageCategory.TRANSPORT, MessageCategory.GOVERNMENT]:
            return True
        
        # Questions about local information
        local_keywords = ['local', 'nearby', 'here', 'this area', 'community', 'city', 'town']
        if any(keyword in text.lower() for keyword in local_keywords):
            return True
        
        return False
    
    def _requires_llm(self, text: str, intent: MessageIntent) -> bool:
        """Determine if message requires LLM processing."""
        # Most messages need LLM processing
        return intent != MessageIntent.UNKNOWN
    
    def _determine_priority(self, intent: MessageIntent, category: MessageCategory, entities: Dict[str, Any]) -> str:
        """Determine message priority."""
        # Emergency messages are always high priority
        if intent == MessageIntent.EMERGENCY or category == MessageCategory.EMERGENCY:
            return "emergency"
        
        # Messages with phone numbers might be important
        if entities.get('phone_numbers'):
            return "high"
        
        # Questions and information requests are normal priority
        if intent in [MessageIntent.QUESTION, MessageIntent.INFORMATION]:
            return "normal"
        
        # Commands are high priority
        if intent == MessageIntent.COMMAND:
            return "high"
        
        # Greetings are low priority
        if intent == MessageIntent.GREETING:
            return "low"
        
        return "normal"
    
    def _calculate_confidence(self, intent_confidence: float, entities: Dict[str, Any]) -> float:
        """Calculate overall parsing confidence."""
        # Base confidence from intent detection
        confidence = intent_confidence
        
        # Boost confidence if we found entities
        if entities.get('phone_numbers'):
            confidence += 0.1
        if entities.get('emails'):
            confidence += 0.05
        if entities.get('keywords'):
            confidence += min(0.2, len(entities['keywords']) * 0.05)
        
        return min(1.0, confidence)
    
    def validate_message(self, message_text: str) -> Dict[str, Any]:
        """Validate message content and format."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check message length
        if len(message_text) > 160:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Message too long: {len(message_text)} characters (max 160)")
        
        if len(message_text) == 0:
            validation_result['valid'] = False
            validation_result['errors'].append("Message is empty")
        
        # Check for profanity
        text_lower = message_text.lower()
        profanity_found = [word for word in self.profanity_words if word in text_lower]
        if profanity_found:
            validation_result['warnings'].append(f"Potentially inappropriate content detected")
        
        # Check for spam patterns
        spam_indicators = ['free', 'win', 'click here', 'limited time', 'act now']
        spam_count = sum(1 for indicator in spam_indicators if indicator in text_lower)
        if spam_count >= 2:
            validation_result['warnings'].append("Message contains potential spam indicators")
        
        # Suggest improvements
        if len(message_text) < 10:
            validation_result['suggestions'].append("Consider providing more context for better assistance")
        
        if not any(char in message_text for char in '?!.'):
            validation_result['suggestions'].append("Consider adding punctuation for clarity")
        
        return validation_result
