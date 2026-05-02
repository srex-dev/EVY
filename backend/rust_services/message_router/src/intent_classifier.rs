//! Rule-based intent classifier
//! 
//! Fast intent classification using keyword matching and patterns

use once_cell::sync::Lazy;
use regex::Regex;
use std::collections::HashSet;

/// Message intent types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Intent {
    Emergency,
    Command,
    Query,
    Greeting,
    Unknown,
}

/// Message priority levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum MessagePriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Emergency = 3,
}

/// Classification result
#[derive(Debug, Clone)]
pub struct ClassificationResult {
    pub intent: Intent,
    pub priority: MessagePriority,
    pub requires_rag: bool,
    pub requires_llm: bool,
    pub confidence: f32,
}

/// Emergency keywords
static EMERGENCY_KEYWORDS: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    let mut set = HashSet::new();
    set.insert("emergency");
    set.insert("help");
    set.insert("urgent");
    set.insert("911");
    set.insert("danger");
    set.insert("fire");
    set.insert("medical");
    set.insert("ambulance");
    set.insert("hospital");
    set.insert("accident");
    set.insert("injured");
    set.insert("bleeding");
    set.insert("heart attack");
    set.insert("stroke");
    set.insert("seizure");
    set
});

/// Question words for RAG detection
static QUESTION_WORDS: Lazy<HashSet<&'static str>> = Lazy::new(|| {
    let mut set = HashSet::new();
    set.insert("what");
    set.insert("where");
    set.insert("when");
    set.insert("who");
    set.insert("why");
    set.insert("how");
    set.insert("which");
    set.insert("?");
    set
});

/// Greeting patterns
static GREETING_PATTERNS: Lazy<Vec<Regex>> = Lazy::new(|| {
    vec![
        Regex::new(r"^(hi|hello|hey|greetings|good morning|good afternoon|good evening)").unwrap(),
        Regex::new(r"^(thanks|thank you|thx)").unwrap(),
    ]
});

/// Command pattern
static COMMAND_PATTERN: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^/").unwrap()
});

/// Rule-based intent classifier
pub struct IntentClassifier {
    emergency_keywords: HashSet<String>,
    question_words: HashSet<String>,
    greeting_patterns: Vec<Regex>,
    command_pattern: Regex,
}

impl IntentClassifier {
    /// Create a new intent classifier
    pub fn new() -> Self {
        let emergency_keywords: HashSet<String> = EMERGENCY_KEYWORDS
            .iter()
            .map(|s| s.to_lowercase())
            .collect();
        
        let question_words: HashSet<String> = QUESTION_WORDS
            .iter()
            .map(|s| s.to_lowercase())
            .collect();
        
        Self {
            emergency_keywords,
            question_words,
            greeting_patterns: GREETING_PATTERNS.clone(),
            command_pattern: COMMAND_PATTERN.clone(),
        }
    }
    
    /// Classify message intent
    pub fn classify(&self, text: &str) -> ClassificationResult {
        let normalized = text.to_lowercase();
        let text_lower = normalized.trim();
        
        // Check for explicit operator commands before keyword matching so
        // command names like /help are not treated as emergencies.
        if self.command_pattern.is_match(text) {
            return ClassificationResult {
                intent: Intent::Command,
                priority: MessagePriority::High,
                requires_rag: false,
                requires_llm: false,
                confidence: 0.95,
            };
        }

        // Check for emergency (highest priority for natural-language messages)
        if self.is_emergency(&text_lower) {
            return ClassificationResult {
                intent: Intent::Emergency,
                priority: MessagePriority::Emergency,
                requires_rag: false,
                requires_llm: false,
                confidence: 0.9,
            };
        }
        
        // Check for greetings
        if self.is_greeting(&text_lower) {
            return ClassificationResult {
                intent: Intent::Greeting,
                priority: MessagePriority::Low,
                requires_rag: false,
                requires_llm: true,
                confidence: 0.8,
            };
        }
        
        // Check if needs RAG (contains questions)
        let needs_rag = self.needs_rag(&text_lower);
        
        // Default to query
        ClassificationResult {
            intent: Intent::Query,
            priority: MessagePriority::Normal,
            requires_rag: needs_rag,
            requires_llm: true,
            confidence: 0.7,
        }
    }
    
    /// Check if message is emergency
    fn is_emergency(&self, text: &str) -> bool {
        for keyword in &self.emergency_keywords {
            if text.contains(keyword) {
                return true;
            }
        }
        false
    }
    
    /// Check if message is greeting
    fn is_greeting(&self, text: &str) -> bool {
        for pattern in &self.greeting_patterns {
            if pattern.is_match(text) {
                return true;
            }
        }
        false
    }
    
    /// Check if message needs RAG (contains questions)
    fn needs_rag(&self, text: &str) -> bool {
        for word in &self.question_words {
            if text.contains(word) {
                return true;
            }
        }
        false
    }
}

impl Default for IntentClassifier {
    fn default() -> Self {
        Self::new()
    }
}

