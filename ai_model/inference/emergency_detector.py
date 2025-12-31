import re

class EmergencyDetector:
    def __init__(self):
        # CRITICAL EMERGENCY WORDS (automatically urgent)
        self.critical_words = [
            'fire', 'explosion', 'shooting', 'drowning', 'heart attack',
            'trapped', 'collapsed', 'casualties', 'evacuate', 'emergency',
            'urgent', 'immediately', 'now', '911', 'sos', 'help',
            'accident', 'injured', 'bleeding', 'unconscious',
            'earthquake', 'tornado', 'tsunami', 'flooding',
            'gas leak', 'chemical', 'radiation', 'hazardous',
            'massive', 'huge', 'big', 'large',  # Emphasizers
        ]
        
        # URGENT PHRASES (automatically urgent)
        self.urgent_phrases = [
            'cannot breathe', 'can\'t breathe', 'trouble breathing',
            'send help', 'need help', 'emergency services',
            'people trapped', 'children trapped', 'person trapped',
            'building burning', 'on fire', 'in flames',
            'call ambulance', 'call police', 'call fire department',
        ]
    
    def detect_emergency(self, text):
        """Detect if text contains emergency keywords"""
        text_lower = text.lower()
        
        critical_count = 0
        for word in self.critical_words:
            if word in text_lower:
                critical_count += 1
        
        urgent_phrase_found = False
        for phrase in self.urgent_phrases:
            if phrase in text_lower:
                urgent_phrase_found = True
                break
        
        # CAPS LOCK detection (people scream in caps)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', text)
        caps_count = len(caps_words)
        
        # Exclamation marks
        exclamation_count = text.count('!')
        
        return {
            'is_emergency': critical_count >= 2 or urgent_phrase_found,
            'critical_count': critical_count,
            'has_urgent_phrase': urgent_phrase_found,
            'caps_words': caps_count,
            'exclamations': exclamation_count,
            'emergency_level': min(100, (critical_count * 20) + (caps_count * 10) + (exclamation_count * 5))
        }