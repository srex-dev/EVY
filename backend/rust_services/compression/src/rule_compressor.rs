//! Rule-based text compressor
//! 
//! Fast compression using abbreviations, regex patterns, and common phrase replacements

use once_cell::sync::Lazy;
use regex::Regex;
use std::collections::HashMap;
use tracing::debug;

/// Abbreviation dictionary for common words/phrases
static ABBREVIATIONS: Lazy<HashMap<&'static str, &'static str>> = Lazy::new(|| {
    let mut map = HashMap::new();
    
    // Common words
    map.insert("the", "");
    map.insert("and", "&");
    map.insert("with", "w/");
    map.insert("without", "w/o");
    map.insert("you", "u");
    map.insert("your", "ur");
    map.insert("are", "r");
    map.insert("be", "b");
    map.insert("to", "2");
    map.insert("too", "2");
    map.insert("for", "4");
    map.insert("for", "4");
    map.insert("before", "b4");
    map.insert("see", "c");
    map.insert("why", "y");
    map.insert("what", "wat");
    map.insert("where", "wer");
    map.insert("when", "wen");
    map.insert("who", "hu");
    map.insert("how", "hw");
    
    // Common phrases
    map.insert("please", "pls");
    map.insert("thanks", "thx");
    map.insert("thank you", "ty");
    map.insert("as soon as possible", "asap");
    map.insert("by the way", "btw");
    map.insert("in my opinion", "imo");
    map.insert("for your information", "fyi");
    map.insert("do not", "don't");
    map.insert("cannot", "can't");
    map.insert("will not", "won't");
    map.insert("would not", "wouldn't");
    map.insert("should not", "shouldn't");
    map.insert("could not", "couldn't");
    
    // Emergency/medical
    map.insert("emergency", "emerg");
    map.insert("hospital", "hosp");
    map.insert("ambulance", "amb");
    map.insert("doctor", "dr");
    map.insert("medical", "med");
    map.insert("medication", "med");
    map.insert("prescription", "rx");
    map.insert("temperature", "temp");
    map.insert("blood pressure", "bp");
    
    // Directions/location
    map.insert("street", "st");
    map.insert("avenue", "ave");
    map.insert("road", "rd");
    map.insert("boulevard", "blvd");
    map.insert("north", "n");
    map.insert("south", "s");
    map.insert("east", "e");
    map.insert("west", "w");
    map.insert("northeast", "ne");
    map.insert("northwest", "nw");
    map.insert("southeast", "se");
    map.insert("southwest", "sw");
    
    // Time
    map.insert("minute", "min");
    map.insert("minutes", "mins");
    map.insert("hour", "hr");
    map.insert("hours", "hrs");
    map.insert("second", "sec");
    map.insert("seconds", "secs");
    
    map
});

/// Pre-compiled regex patterns for compression
static COMPRESSION_PATTERNS: Lazy<Vec<(Regex, &'static str)>> = Lazy::new(|| {
    vec![
        // Remove extra whitespace
        (Regex::new(r"\s+").unwrap(), " "),
        // Remove leading/trailing whitespace
        (Regex::new(r"^\s+|\s+$").unwrap(), ""),
        // Compress common patterns
        (Regex::new(r"\bdo not\b").unwrap(), "don't"),
        (Regex::new(r"\bcannot\b").unwrap(), "can't"),
        (Regex::new(r"\bwill not\b").unwrap(), "won't"),
        (Regex::new(r"\bwould not\b").unwrap(), "wouldn't"),
        (Regex::new(r"\bshould not\b").unwrap(), "shouldn't"),
        (Regex::new(r"\bcould not\b").unwrap(), "couldn't"),
        // Remove articles in some contexts
        (Regex::new(r"\bthe\s+").unwrap(), ""),
        (Regex::new(r"\ba\s+").unwrap(), ""),
        (Regex::new(r"\ban\s+").unwrap(), ""),
    ]
});

/// Rule-based compressor
pub struct RuleBasedCompressor {
    abbreviations: HashMap<String, String>,
    patterns: Vec<(Regex, String)>,
}

impl RuleBasedCompressor {
    /// Create a new rule-based compressor
    pub fn new() -> Self {
        let abbreviations: HashMap<String, String> = ABBREVIATIONS
            .iter()
            .map(|(k, v)| (k.to_lowercase(), v.to_string()))
            .collect();
        
        let patterns: Vec<(Regex, String)> = COMPRESSION_PATTERNS
            .iter()
            .map(|(re, repl)| (re.clone(), repl.to_string()))
            .collect();
        
        Self {
            abbreviations,
            patterns,
        }
    }
    
    /// Compress text to target length
    pub fn compress(&self, text: &str, target_length: usize) -> String {
        if text.len() <= target_length {
            return text.to_string();
        }
        
        let mut compressed = text.to_lowercase();
        
        // Apply regex patterns
        for (pattern, replacement) in &self.patterns {
            compressed = pattern.replace_all(&compressed, replacement.as_str()).to_string();
        }
        
        // Apply abbreviations (longest first to avoid partial matches)
        let mut sorted_abbrevs: Vec<_> = self.abbreviations.iter().collect();
        sorted_abbrevs.sort_by(|a, b| b.0.len().cmp(&a.0.len()));
        
        for (word, abbrev) in sorted_abbrevs {
            if compressed.len() <= target_length {
                break;
            }
            
            let pattern = format!(r"\b{}\b", regex::escape(word));
            if let Ok(re) = Regex::new(&pattern) {
                compressed = re.replace_all(&compressed, abbrev.as_str()).to_string();
            }
        }
        
        // If still too long, truncate intelligently
        if compressed.len() > target_length {
            compressed = self.intelligent_truncate(&compressed, target_length);
        }
        
        debug!("Compressed {} -> {} chars (target: {})", text.len(), compressed.len(), target_length);
        compressed
    }
    
    /// Intelligently truncate text at word boundaries
    fn intelligent_truncate(&self, text: &str, max_len: usize) -> String {
        if text.len() <= max_len {
            return text.to_string();
        }
        
        // Try to truncate at sentence boundary
        if let Some(pos) = text[..max_len.min(text.len())].rfind('.') {
            if pos > max_len * 2 / 3 {
                return text[..=pos].trim().to_string();
            }
        }
        
        // Try to truncate at word boundary
        if let Some(pos) = text[..max_len.min(text.len())].rfind(' ') {
            if pos > max_len * 2 / 3 {
                return format!("{}...", text[..pos].trim());
            }
        }
        
        // Hard truncate
        format!("{}...", &text[..max_len.saturating_sub(3)])
    }
    
    /// Get compression ratio
    pub fn compression_ratio(&self, original: &str, compressed: &str) -> f32 {
        if original.is_empty() {
            return 0.0;
        }
        let ratio = compressed.len() as f32 / original.len() as f32;
        (1.0 - ratio) * 100.0
    }
}

impl Default for RuleBasedCompressor {
    fn default() -> Self {
        Self::new()
    }
}

