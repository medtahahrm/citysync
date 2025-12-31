import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import re

def clean_text(text):
    """Clean text for inference"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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

class ReportClassifier:
    def __init__(self, model_path='ai_model/models'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.emergency_detector = EmergencyDetector()
        
        # Load model
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.model.to(self.device)
            self.model.eval()
            print("✅ Trained model loaded successfully")
        except Exception as e:
            print(f"⚠️  Could not load trained model: {e}")
            print("Using default BERT model...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                'bert-base-uncased', 
                num_labels=2
            )
            self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.model.to(self.device)
            self.model.eval()
    
    def predict(self, text, threshold=0.5):  # Lower threshold to 0.5
        """Predict urgency with emergency detection"""
        
        # 1. First check for obvious emergencies
        emergency_check = self.emergency_detector.detect_emergency(text)
        
        # DEBUG: Print emergency detection
        # print(f"🔍 Emergency check: {emergency_check}")
        
        # If clear emergency, override AI
        if emergency_check['is_emergency']:
            # Calculate urgency score based on emergency level
            urgency_score = min(1.0, 0.7 + (emergency_check['emergency_level'] / 100))
            
            # FORCE URGENT for fire with people trapped/can't breathe
            text_lower = text.lower()
            if 'fire' in text_lower and ('trapped' in text_lower or "can't breathe" in text_lower or "cannot breathe" in text_lower):
                urgency_score = 0.95
            
            return {
                'is_urgent': True,
                'urgency_score': urgency_score,
                'confidence': 0.95,
                'confidence_level': 'high',
                'emergency_override': True,
                'emergency_details': emergency_check
            }
        
        # 2. Otherwise use AI
        cleaned_text = clean_text(text)
        
        # Tokenize
        inputs = self.tokenizer(
            cleaned_text,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            probabilities = F.softmax(outputs.logits, dim=1)
        
        # Get scores
        urgent_prob = probabilities[0][1].item()
        
        # Apply emergency boost if any emergency indicators
        if emergency_check['critical_count'] > 0:
            urgent_prob = min(1.0, urgent_prob + (emergency_check['critical_count'] * 0.2))
        
        # Make prediction
        prediction = 1 if urgent_prob >= threshold else 0
        
        return {
            'is_urgent': bool(prediction),
            'urgency_score': urgent_prob,
            'confidence': urgent_prob if prediction else 1 - urgent_prob,
            'confidence_level': 'high' if urgent_prob > 0.8 or urgent_prob < 0.2 else 'medium',
            'emergency_override': False,
            'emergency_details': emergency_check
        }

# Simple test if run directly
if __name__ == "__main__":
    print("🧪 Testing ReportClassifier...")
    
    classifier = ReportClassifier()
    
    test_reports = [
        "massive fire in the building people can't breathe no more please send help",
        "Fire emergency! Building on fire, people trapped!",
        "Street light not working",
        "Garbage not collected",
    ]
    
    for report in test_reports:
        result = classifier.predict(report)
        print(f"\n📝 {report[:50]}...")
        print(f"   Urgent: {'🔴 YES' if result['is_urgent'] else '🟢 NO'}")
        print(f"   Score: {result['urgency_score']:.2%}")
        print(f"   Emergency Override: {result.get('emergency_override', False)}")