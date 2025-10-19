import json
import random
import re
from datetime import datetime
from typing import List, Dict

class AdvancedTrainingGenerator:
    def __init__(self):
        self.phishing_templates = self._load_phishing_templates()
        self.legitimate_templates = self._load_legitimate_templates()
    
    def _load_phishing_templates(self) -> List[Dict]:
        """Load realistic phishing templates based on real-world patterns"""
        return [
            {
                "template": "URGENT: Your {platform} account shows suspicious login attempts from {location}. To prevent immediate suspension, verify your identity at: {link}",
                "platforms": ["LinkedIn", "Facebook", "Google", "Microsoft", "Apple"],
                "locations": ["China", "Russia", "Nigeria", "unknown location", "new device"],
                "tags": ["urgency", "authority", "suspicious_activity"]
            },
            {
                "template": "Security Alert: Unusual activity detected on your account. Click to secure: {link} This is mandatory to avoid permanent termination.",
                "platforms": ["bank", "email", "social media", "cloud storage"],
                "tags": ["authority", "fear", "mandatory_action"]
            },
            {
                "template": "Investment Opportunity: Get {return}% returns on your investment. Limited time offer! Contact me on {platform} at {contact}",
                "return": ["300", "500", "1000", "2000"],
                "platforms": ["WhatsApp", "Telegram", "Signal", "WeChat"],
                "contact": ["this number", "my personal number", "the provided contact"],
                "tags": ["financial", "scarcity", "platform_migration"]
            },
            {
                "template": "You've been selected for a exclusive {offer}! To claim your prize, provide your personal information at: {link}",
                "offer": ["prize", "reward", "bonus", "special offer", "limited opportunity"],
                "tags": ["exclusivity", "personal_info", "reward"]
            },
            {
                "template": "Official Notice: Your {service} requires immediate verification due to policy updates. Failure to comply within {timeframe} will result in {consequence}",
                "service": ["account", "subscription", "membership", "service"],
                "timeframe": ["24 hours", "2 hours", "immediately", "today"],
                "consequence": ["suspension", "termination", "legal action", "fees"],
                "tags": ["authority", "urgency", "consequences"]
            }
        ]
    
    def _load_legitimate_templates(self) -> List[Dict]:
        """Load legitimate professional message templates"""
        return [
            {
                "template": "Hi {name}, I came across your profile and was impressed by your work in {field}. Would you be open to connecting?",
                "fields": ["tech", "marketing", "finance", "engineering", "design"],
                "tags": ["professional", "networking"]
            },
            {
                "template": "Enjoyed your recent post about {topic}! I particularly liked your point about {detail}",
                "topics": ["AI", "leadership", "innovation", "industry trends", "technology"],
                "details": ["the future impact", "practical applications", "your insights", "the analysis"],
                "tags": ["engagement", "professional"]
            },
            {
                "template": "Would you be available for a quick chat about {subject} next week? I'd love to get your perspective",
                "subjects": ["industry developments", "potential collaboration", "professional interests", "mutual connections"],
                "tags": ["professional", "meeting_request"]
            },
            {
                "template": "Thanks for connecting! I look forward to seeing your content and learning from your experience in {industry}",
                "industries": ["technology", "business", "healthcare", "education", "finance"],
                "tags": ["professional", "gratitude"]
            }
        ]
    
    def generate_phishing_sample(self) -> str:
        """Generate a realistic phishing message"""
        template_data = random.choice(self.phishing_templates)
        template = template_data["template"]
        
        # Fill in template variables
        if "{platform}" in template:
            template = template.replace("{platform}", random.choice(template_data["platforms"]))
        if "{location}" in template:
            template = template.replace("{location}", random.choice(template_data["locations"]))
        if "{link}" in template:
            template = template.replace("{link}", f"http://verify-{random.randint(1000,9999)}.com")
        if "{return}" in template:
            template = template.replace("{return}", random.choice(template_data["return"]))
        if "{platform}" in template and "platforms" in template_data:
            template = template.replace("{platform}", random.choice(template_data["platforms"]))
        if "{contact}" in template:
            template = template.replace("{contact}", random.choice(template_data["contact"]))
        if "{offer}" in template:
            template = template.replace("{offer}", random.choice(template_data["offer"]))
        if "{service}" in template:
            template = template.replace("{service}", random.choice(template_data["service"]))
        if "{timeframe}" in template:
            template = template.replace("{timeframe}", random.choice(template_data["timeframe"]))
        if "{consequence}" in template:
            template = template.replace("{consequence}", random.choice(template_data["consequence"]))
        
        return template
    
    def generate_legitimate_sample(self) -> str:
        """Generate a legitimate professional message"""
        template_data = random.choice(self.legitimate_templates)
        template = template_data["template"]
        
        # Fill in template variables
        if "{name}" in template:
            template = template.replace("{name}", random.choice(["", "there", ""]))  # Often omitted in LinkedIn
        if "{field}" in template:
            template = template.replace("{field}", random.choice(template_data["fields"]))
        if "{topic}" in template:
            template = template.replace("{topic}", random.choice(template_data["topics"]))
        if "{detail}" in template:
            template = template.replace("{detail}", random.choice(template_data["details"]))
        if "{subject}" in template:
            template = template.replace("{subject}", random.choice(template_data["subjects"]))
        if "{industry}" in template:
            template = template.replace("{industry}", random.choice(template_data["industries"]))
        
        return template
    
    def generate_dataset(self, size: int = 2000) -> List[Dict]:
        """Generate balanced training dataset"""
        dataset = []
        
        for i in range(size):
            if i % 2 == 0:
                # Generate phishing sample
                text = self.generate_phishing_sample()
                dataset.append({
                    "text": text,
                    "label": 1,
                    "type": "phishing",
                    "source": "generated"
                })
            else:
                # Generate legitimate sample
                text = self.generate_legitimate_sample()
                dataset.append({
                    "text": text,
                    "label": 0,
                    "type": "legitimate", 
                    "source": "generated"
                })
        
        # Add some real-world pattern variations
        self._add_real_world_variations(dataset)
        
        return dataset
    
    def _add_real_world_variations(self, dataset: List[Dict]):
        """Add realistic variations to make training data more robust"""
        variations = [
            "Kindly ",
            "Please be advised ",
            "Important: ",
            "Attention: ",
            "Hello, ",
            "Hi there, ",
            "Greetings, ",
            ""
        ]
        
        for item in random.sample(dataset, len(dataset) // 4):  # 25% of samples
            variation = random.choice(variations)
            if variation and not item['text'].startswith(tuple(variations)):
                item['text'] = variation + item['text']
    
    def save_dataset(self, dataset: List[Dict], filepath: str = "data/advanced_training_dataset.json"):
        """Save generated dataset"""
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        # Print statistics
        phishing_count = sum(1 for item in dataset if item['label'] == 1)
        legitimate_count = sum(1 for item in dataset if item['label'] == 0)
        
        print(f"✅ Generated {len(dataset)} training samples")
        print(f"📊 Phishing: {phishing_count}, Legitimate: {legitimate_count}")
        print(f"💾 Saved to {filepath}")