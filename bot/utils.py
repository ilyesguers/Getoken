"""
Utility functions for the bot
"""
import random
import time
import string
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from loguru import logger


class Utils:
    """Utility functions for various operations"""
    
    @staticmethod
    def random_delay(min_seconds: int = 30, max_seconds: int = 120):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {delay:.1f} seconds")
        time.sleep(delay)
    
    @staticmethod
    def generate_random_string(length: int = 10, include_numbers: bool = True) -> str:
        """Generate random string for passwords/emails"""
        chars = string.ascii_lowercase
        if include_numbers:
            chars += string.digits
        
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_temp_email(domain: str = "mailinator.com") -> str:
        """Generate temporary email address"""
        username = Utils.generate_random_string(10, include_numbers=True)
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_password(length: int = 16) -> str:
        """Generate strong random password"""
        # Mix of uppercase, lowercase, numbers, and symbols
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        
        # Ensure at least one of each type
        password = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*"),
        ]
        
        # Fill the rest
        password += [random.choice(chars) for _ in range(length - 4)]
        
        # Shuffle
        random.shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def generate_birth_date(min_age: int = 20, max_age: int = 50) -> str:
        """Generate random birth date in DD/MM/YYYY format"""
        today = datetime.now()
        age = random.randint(min_age, max_age)
        
        # Calculate birth year
        birth_year = today.year - age
        
        # Random month and day
        birth_month = random.randint(1, 12)
        
        # Days in month (simplified)
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:  # February
            max_day = 28
        
        birth_day = random.randint(1, max_day)
        
        return f"{birth_day:02d}/{birth_month:02d}/{birth_year}"
    
    @staticmethod
    def generate_profile_id() -> str:
        """Generate unique profile ID"""
        timestamp = str(int(time.time()))
        random_str = Utils.generate_random_string(8, include_numbers=True)
        combined = f"{timestamp}{random_str}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    @staticmethod
    def simulate_typing_speed(text: str, wpm: int = 35):
        """Simulate human typing speed"""
        words = len(text.split())
        minutes = words / wpm
        seconds = minutes * 60
        
        # Add some randomness
        actual_seconds = seconds * random.uniform(0.8, 1.2)
        
        logger.debug(f"Simulating typing: {len(text)} chars, ~{actual_seconds:.1f}s")
        time.sleep(actual_seconds)
    
    @staticmethod
    def add_human_error(text: str, error_probability: float = 0.1) -> str:
        """Add realistic human errors to text"""
        if random.random() > error_probability:
            return text
        
        # Common mistakes
        mistakes = {
            'ا': 'أ',
            'ة': 'ه',
            'ى': 'ي',
            'ء': 'ئ',
        }
        
        text_list = list(text)
        
        # Make 1-2 mistakes
        num_mistakes = random.randint(1, 2)
        for _ in range(num_mistakes):
            if len(text_list) < 3:
                break
                
            idx = random.randint(0, len(text_list) - 1)
            char = text_list[idx]
            
            if char in mistakes:
                text_list[idx] = mistakes[char]
        
        # Sometimes correct the mistake (70% of the time)
        if random.random() < 0.7 and len(text_list) > 3:
            # Delete one character and retype
            idx = random.randint(0, len(text_list) - 1)
            text_list.pop(idx)
        
        return ''.join(text_list)
    
    @staticmethod
    def generate_random_scroll_pause() -> float:
        """Generate random scroll pause time"""
        return random.uniform(2.0, 8.0)
    
    @staticmethod
    def should_make_error(error_probability: float = 0.1) -> bool:
        """Determine if we should simulate a human error"""
        return random.random() < error_probability
    
    @staticmethod
    def get_random_city(cities: List[str]) -> str:
        """Get random city from list"""
        return random.choice(cities)
    
    @staticmethod
    def format_timestamp(dt: Optional[datetime] = None) -> str:
        """Format datetime to ISO string"""
        if dt is None:
            dt = datetime.now()
        return dt.isoformat()
    
    @staticmethod
    def is_time_for_action(last_action_time: datetime, interval_hours: int) -> bool:
        """Check if enough time has passed for next action"""
        if last_action_time is None:
            return True
        
        elapsed = datetime.now() - last_action_time
        required = timedelta(hours=interval_hours)
        
        return elapsed >= required
    
    @staticmethod
    def calculate_maturity_date(created_at: datetime, maturity_days: int) -> datetime:
        """Calculate when account will be mature"""
        return created_at + timedelta(days=maturity_days)
    
    @staticmethod
    def is_account_mature(created_at: datetime, maturity_days: int) -> bool:
        """Check if account has matured"""
        maturity_date = Utils.calculate_maturity_date(created_at, maturity_days)
        return datetime.now() >= maturity_date
