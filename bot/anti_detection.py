"""
Advanced Anti-Detection System v2.0
Enterprise-grade anti-detection for Facebook automation
"""
import random
import time
import hashlib
import json
import math
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from loguru import logger
from fake_useragent import UserAgent

from bot.config import BotConfig
from bot.browser_fingerprint import BrowserFingerprint
from bot.behavior_patterns import BehaviorPattern


class AntiDetectionV2:
    """
    Advanced anti-detection system with:
    - Realistic browser fingerprints
    - Human behavior simulation
    - Mouse movement patterns
    - Typing pattern simulation
    - Session management
    - Activity cycling
    - Pattern breaking
    """
    
    def __init__(self, account_id: int = 0, proxy: Optional[Dict] = None):
        self.account_id = account_id
        self.proxy = proxy
        self.config = BotConfig
        
        # Generate unique fingerprint
        self.fingerprint = BrowserFingerprint(seed=f"account_{account_id}")
        
        # Generate behavior pattern
        self.behavior = BehaviorPattern(account_id=account_id)
        
        # Session tracking
        self.session_start = None
        self.session_actions = 0
        self.session_duration = 0
        self.last_action_time = None
        self.last_action_type = None
        
        # State tracking
        self.is_active = False
        self.current_page_type = None
        self.page_history = []
        
        # Anti-pattern tracking
        self.action_intervals = []
        self.timing_pattern = []
        
        # User agent
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None
        
        logger.debug(f"AntiDetection V2 initialized for account {account_id}")
    
    def start_session(self):
        """Start a new browsing session"""
        self.session_start = datetime.now()
        self.session_actions = 0
        self.is_active = True
        self.page_history = []
        logger.info(f"Session started for account {self.account_id}")
    
    def end_session(self):
        """End current session"""
        if self.session_start:
            duration = datetime.now() - self.session_start
            logger.info(
                f"Session ended. Duration: {duration.total_seconds():.0f}s, "
                f"Actions: {self.session_actions}"
            )
        self.is_active = False
        self.session_start = None
        self.session_actions = 0
    
    def get_random_user_agent(self) -> str:
        """Get randomized user agent"""
        if self.ua:
            try:
                return self.ua.random
            except Exception:
                pass
        
        # Fallback with detailed agents
        agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Mac Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            # Linux Chrome
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            # Mobile Chrome
            "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
            # Mobile Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
            # Opera
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
        ]
        return random.choice(agents)
    
    def human_delay(self, min_sec: int = None, max_sec: int = None, context: str = "general"):
        """
        Advanced human-like delay with multiple distributions
        """
        if min_sec is None:
            min_sec = self.config.MIN_DELAY_SECONDS
        if max_sec is None:
            max_sec = self.config.MAX_DELAY_SECONDS
        
        # Different delay distributions based on context
        if context == "action_to_action":
            # Short delay between actions
            delay = self._gaussian_delay(min_sec, max_sec)
        elif context == "page_load":
            # Medium delay after page load
            delay = self._log_normal_delay(min_sec, max_sec)
        elif context == "reading":
            # Long delay for reading
            delay = self._exponential_delay(min_sec, max_sec)
        elif context == "distraction":
            # Very long delay for distraction
            delay = self._uniform_delay(min_sec * 3, max_sec * 5)
        else:
            # Mixed distribution
            delay = self._mixed_delay(min_sec, max_sec)
        
        # Apply personality modifier
        patience = self.behavior.personality["patience_level"]
        delay *= (0.7 + patience * 0.6)
        
        # Occasionally add longer pauses
        if random.random() < 0.05:  # 5% chance
            delay *= random.uniform(2.0, 5.0)
            logger.debug(f"Extended pause: {delay:.1f}s")
        
        # Track timing pattern
        self.timing_pattern.append(delay)
        self._check_timing_pattern()
        
        logger.debug(f"Delay: {delay:.1f}s (context: {context})")
        time.sleep(delay)
    
    def _gaussian_delay(self, min_sec: int, max_sec: int) -> float:
        """Gaussian distribution delay"""
        mean = (min_sec + max_sec) / 2
        std = (max_sec - min_sec) / 6
        return max(min_sec, min(max_sec, random.gauss(mean, std)))
    
    def _log_normal_delay(self, min_sec: int, max_sec: int) -> float:
        """Log-normal distribution (more realistic for human delays)"""
        mu = math.log((min_sec + max_sec) / 2)
        sigma = 0.5
        delay = random.lognormvariate(mu, sigma)
        return max(min_sec, min(max_sec, delay))
    
    def _exponential_delay(self, min_sec: int, max_sec: int) -> float:
        """Exponential distribution (for reading/waiting)"""
        lambd = 1.0 / ((min_sec + max_sec) / 2)
        delay = random.expovariate(lambd)
        return max(min_sec, min(max_sec, delay))
    
    def _uniform_delay(self, min_sec: int, max_sec: int) -> float:
        """Uniform distribution"""
        return random.uniform(min_sec, max_sec)
    
    def _mixed_delay(self, min_sec: int, max_sec: int) -> float:
        """Mixed distribution (randomly chooses between distributions)"""
        choice = random.random()
        if choice < 0.4:
            return self._gaussian_delay(min_sec, max_sec)
        elif choice < 0.7:
            return self._log_normal_delay(min_sec, max_sec)
        elif choice < 0.9:
            return self._exponential_delay(min_sec, max_sec)
        else:
            return self._uniform_delay(min_sec, max_sec)
    
    def micro_delay(self):
        """Very short delay for rapid actions"""
        time.sleep(random.uniform(0.1, 0.8))
    
    def _check_timing_pattern(self):
        """Check if timing pattern is too regular and break it"""
        if len(self.timing_pattern) < 5:
            return
        
        recent = self.timing_pattern[-5:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        
        # If pattern is too regular (low variance), add randomness
        if variance < (mean * 0.1) ** 2:
            logger.debug("Breaking timing pattern - too regular")
            # Add a significantly different delay next time
            self.timing_pattern.append(mean * random.uniform(2, 5))
    
    def simulate_mouse_movement(self, target_x: int, target_y: int) -> List[Tuple[int, int]]:
        """Generate realistic mouse movement path"""
        # Start from random position
        start_x = random.randint(100, 800)
        start_y = random.randint(100, 600)
        
        return self.behavior.generate_mouse_path(
            (start_x, start_y),
            (target_x, target_y)
        )
    
    def simulate_typing(self, text: str) -> float:
        """
        Simulate typing text and return total time
        """
        sequence = self.behavior.generate_typing_sequence(text)
        total_time = 0
        
        for step in sequence:
            delay = step.get("delay", 0.1)
            total_time += delay
        
        logger.debug(f"Typing simulation: {len(text)} chars, ~{total_time:.1f}s")
        return total_time
    
    def should_take_break(self) -> bool:
        """Determine if bot should take a natural break"""
        # Based on session duration
        if self.session_start:
            elapsed = (datetime.now() - self.session_start).total_seconds()
            if elapsed > random.uniform(900, 2700):  # 15-45 min
                return True
        
        # Based on action count
        if self.session_actions > random.randint(8, 15):
            return True
        
        return False
    
    def take_break(self):
        """Take a natural break"""
        break_time = random.uniform(120, 600)  # 2-10 minutes
        logger.info(f"Taking a break for {break_time/60:.1f} minutes")
        time.sleep(break_time)
        self.session_actions = 0
    
    def get_natural_navigation(self, target_url: str) -> List[str]:
        """Get natural navigation path to target"""
        return self.behavior.behavior.personality.get("preferred_paths", [
            "home", "newsfeed", "target"
        ])
    
    def simulate_reading(self, content_length: int = 500):
        """Simulate reading content"""
        read_time = self.behavior.simulate_reading_time(content_length)
        logger.debug(f"Simulating reading: {read_time:.1f}s")
        
        # Add some pauses during reading
        pauses = random.randint(1, 4)
        time_per_segment = read_time / pauses
        
        for i in range(pauses):
            time.sleep(time_per_segment)
            # Maybe scroll a bit
            if random.random() < 0.5:
                self.micro_delay()
    
    def simulate_distraction(self):
        """Simulate user getting distracted"""
        if not self.behavior.should_get_distracted():
            return
        
        distraction = self.behavior.get_distraction_action()
        logger.debug(f"Distraction: {distraction}")
        
        if distraction == "check_phone":
            time.sleep(random.uniform(30, 120))
        elif distraction == "look_away":
            time.sleep(random.uniform(10, 30))
        elif distraction == "switch_tab":
            time.sleep(random.uniform(5, 20))
    
    def record_action(self, action_type: str = "general"):
        """Record that an action was performed"""
        now = datetime.now()
        
        if self.last_action_time:
            interval = (now - self.last_action_time).total_seconds()
            self.action_intervals.append(interval)
        
        self.last_action_time = now
        self.last_action_type = action_type
        self.session_actions += 1
        
        self.behavior.record_action(action_type)
    
    def should_vary_behavior(self) -> bool:
        """Determine if behavior should vary"""
        return random.random() < 0.3  # 30% chance
    
    def get_session_info(self) -> Dict:
        """Get current session information"""
        return {
            "account_id": self.account_id,
            "session_start": self.session_start,
            "session_actions": self.session_actions,
            "is_active": self.is_active,
            "timing_patterns": len(self.timing_pattern),
            "fingerprint_hash": self.fingerprint.get_hash(),
        }
    
    def get_stealth_config(self) -> Dict:
        """Get complete stealth configuration"""
        return {
            "user_agent": self.get_random_user_agent(),
            "fingerprint": self.fingerprint.to_dict(),
            "stealth_script": self.fingerprint.get_stealth_script(),
            "viewport": {
                "width": self.fingerprint.fingerprint["screen"]["width"],
                "height": self.fingerprint.fingerprint["screen"]["height"],
            },
            "locale": "ar-DZ",
            "timezone": self.fingerprint.fingerprint["timezone"],
        }
    
    def anti_fingerprint_check(self) -> bool:
        """Perform anti-fingerprint checks"""
        # Check if behavior is too regular
        if len(self.action_intervals) >= 5:
            recent = self.action_intervals[-5:]
            mean = sum(recent) / len(recent)
            variance = sum((x - mean) ** 2 for x in recent) / len(recent)
            
            # If too regular, add randomness
            if variance < 1.0:
                logger.warning("Behavior too regular - adding randomness")
                time.sleep(random.uniform(5, 30))
                return False
        
        return True
    
    def perform_idle_actions(self):
        """Perform some idle actions to look natural"""
        actions_count = random.randint(1, 3)
        
        for _ in range(actions_count):
            action = random.choice([
                "scroll_down",
                "scroll_up",
                "move_mouse",
                "hover_element",
                "wait",
            ])
            
            if action == "scroll_down":
                time.sleep(random.uniform(0.5, 2))
            elif action == "scroll_up":
                time.sleep(random.uniform(0.5, 1.5))
            elif action == "move_mouse":
                time.sleep(random.uniform(0.3, 1))
            elif action == "hover_element":
                time.sleep(random.uniform(1, 3))
            elif action == "wait":
                time.sleep(random.uniform(2, 8))
    
    def check_detection_risk(self) -> Dict:
        """Check current detection risk level"""
        risk_factors = {
            "timing_regularity": 0,
            "session_length": 0,
            "action_frequency": 0,
            "pattern_repetition": 0,
        }
        
        # Check timing regularity
        if len(self.action_intervals) >= 3:
            recent = self.action_intervals[-3:]
            mean = sum(recent) / len(recent)
            if mean > 0:
                variance = sum((x - mean) ** 2 for x in recent) / len(recent)
                cv = (variance ** 0.5) / mean  # coefficient of variation
                risk_factors["timing_regularity"] = max(0, 1 - cv)
        
        # Check session length
        if self.session_start:
            elapsed = (datetime.now() - self.session_start).total_seconds()
            if elapsed > 3600:  # 1 hour
                risk_factors["session_length"] = min(1, (elapsed - 3600) / 3600)
        
        # Check action frequency
        if self.session_actions > 20:
            risk_factors["action_frequency"] = min(1, (self.session_actions - 20) / 30)
        
        # Overall risk
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        risk_level = "low"
        if overall_risk > 0.7:
            risk_level = "high"
        elif overall_risk > 0.4:
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "overall_score": overall_risk,
            "factors": risk_factors,
        }
    
    def take_evasive_action(self):
        """Take action to reduce detection risk"""
        risk = self.check_detection_risk()
        
        if risk["risk_level"] == "high":
            logger.warning("High detection risk - taking evasive action")
            # Long break
            time.sleep(random.uniform(300, 900))  # 5-15 min
            # Reset patterns
            self.timing_pattern = []
            self.action_intervals = []
            self.session_actions = 0
        
        elif risk["risk_level"] == "medium":
            logger.info("Medium detection risk - slowing down")
            time.sleep(random.uniform(60, 180))  # 1-3 min
