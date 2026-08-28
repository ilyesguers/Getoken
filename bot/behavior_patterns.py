"""
Advanced Behavior Patterns
Simulates realistic human browsing behavior
"""
import random
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger


class BehaviorPattern:
    """
    Advanced behavior pattern generator
    Creates realistic sequences of actions
    """
    
    # Common browsing sessions
    BROWSING_SESSIONS = {
        "casual": {
            "duration_minutes": (5, 30),
            "scroll_count": (5, 20),
            "click_count": (1, 5),
            "pause_between": (2, 10),
        },
        "focused": {
            "duration_minutes": (1, 10),
            "scroll_count": (2, 8),
            "click_count": (3, 10),
            "pause_between": (1, 5),
        },
        " distracted": {
            "duration_minutes": (10, 60),
            "scroll_count": (3, 15),
            "click_count": (0, 3),
            "pause_between": (10, 60),
        },
        "shopping": {
            "duration_minutes": (10, 45),
            "scroll_count": (10, 30),
            "click_count": (5, 15),
            "pause_between": (3, 15),
        },
    }
    
    # Mouse movement patterns
    MOUSE_MOVEMENTS = {
        "direct": {"speed": (200, 500), "curves": 0},
        "curved": {"speed": (100, 300), "curves": (1, 3)},
        "hesitant": {"speed": (50, 200), "curves": (2, 5)},
    }
    
    # Scroll patterns
    SCROLL_PATTERNS = {
        "quick_read": {"scroll_size": (300, 800), "pause": (1, 3), "total": (3, 8)},
        "careful_read": {"scroll_size": (100, 300), "pause": (3, 10), "total": (10, 30)},
        "skimming": {"scroll_size": (500, 1200), "pause": (0.5, 2), "total": (5, 15)},
        "deep_read": {"scroll_size": (50, 200), "pause": (5, 20), "total": (15, 40)},
    }
    
    # Typing patterns
    TYPING_PATTERNS = {
        "fast": {"wpm": (40, 60), "error_rate": 0.02, "backspace_rate": 0.05},
        "average": {"wpm": (25, 40), "error_rate": 0.05, "backspace_rate": 0.10},
        "slow": {"wpm": (15, 25), "error_rate": 0.08, "backspace_rate": 0.15},
        "hunt_peck": {"wpm": (10, 20), "error_rate": 0.10, "backspace_rate": 0.20},
    }
    
    def __init__(self, account_id: int = 0):
        self.account_id = account_id
        self.rng = random.Random(account_id + int(datetime.now().timestamp()))
        self.personality = self._generate_personality()
        self.session_history: List[Dict] = []
        self.action_count = 0
    
    def _generate_personality(self) -> Dict:
        """Generate consistent personality traits for this account"""
        return {
            "preferred_session_type": self.rng.choice(list(self.BROWSING_SESSIONS.keys())),
            "typical_active_hours": self._generate_active_hours(),
            "typing_speed": self.rng.choice(list(self.TYPING_PATTERNS.keys())),
            "mouse_style": self.rng.choice(list(self.MOUSE_MOVEMENTS.keys())),
            "scroll_style": self.rng.choice(list(self.SCROLL_PATTERS.keys())),
            "attention_span": self.rng.uniform(0.5, 1.5),
            "distraction_rate": self.rng.uniform(0.02, 0.15),
            "curiosity_level": self.rng.uniform(0.3, 1.0),
            "patience_level": self.rng.uniform(0.3, 1.0),
            "social_tendency": self.rng.uniform(0.2, 0.9),
        }
    
    def _generate_active_hours(self) -> Tuple[int, int]:
        """Generate typical active hours for this user"""
        start = self.rng.randint(6, 12)
        end = self.rng.randint(start + 6, min(start + 14, 23))
        return (start, end)
    
    def is_active_time(self) -> bool:
        """Check if current time is within user's active hours"""
        current_hour = datetime.now().hour
        start, end = self.personality["typical_active_hours"]
        return start <= current_hour <= end
    
    def get_next_action_delay(self, context: str = "browsing") -> float:
        """Calculate delay before next action based on personality"""
        base_delays = {
            "browsing": (2, 10),
            "typing": (0.1, 0.5),
            "clicking": (0.5, 2),
            "reading": (5, 30),
            "decision": (3, 15),
        }
        
        min_delay, max_delay = base_delays.get(context, (2, 10))
        
        # Apply personality modifiers
        patience = self.personality["patience_level"]
        distraction = self.personality["distraction_rate"]
        
        # More patient = longer delays possible
        max_delay *= (0.5 + patience)
        
        # Distracted users have more variable delays
        if self.rng.random() < distraction:
            max_delay *= self.rng.uniform(2, 5)
        
        delay = self.rng.uniform(min_delay, max_delay)
        
        return delay
    
    def generate_mouse_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate realistic mouse movement path"""
        style = self.MOUSE_MOVEMENTS[self.personality["mouse_style"]]
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = (dx**2 + dy**2) ** 0.5
        
        # Number of steps based on distance and speed
        speed = self.rng.uniform(*style["speed"]) if isinstance(style["speed"], tuple) else style["speed"]
        steps = max(int(distance / speed), 5)
        
        path = []
        num_curves = self.rng.randint(*style["curves"]) if isinstance(style["curves"], tuple) else style["curves"]
        
        # Generate control points for curves
        control_points = []
        for _ in range(num_curves):
            cx = start[0] + dx * self.rng.uniform(0.2, 0.8) + self.rng.uniform(-100, 100)
            cy = start[1] + dy * self.rng.uniform(0.2, 0.8) + self.rng.uniform(-100, 100)
            control_points.append((cx, cy))
        
        # Interpolate path
        for i in range(steps + 1):
            t = i / steps
            # Bezier curve through control points
            if not control_points:
                x = start[0] + dx * t
                y = start[1] + dy * t
            else:
                # Simple curve through first control point
                cp = control_points[0]
                x = (1-t)**2 * start[0] + 2*(1-t)*t * cp[0] + t**2 * end[0]
                y = (1-t)**2 * start[1] + 2*(1-t)*t * cp[1] + t**2 * end[1]
            
            # Add small jitter
            x += self.rng.uniform(-2, 2)
            y += self.rng.uniform(-2, 2)
            
            path.append((int(x), int(y)))
        
        return path
    
    def generate_typing_sequence(self, text: str) -> List[Dict]:
        """Generate realistic typing sequence with errors and corrections"""
        pattern = self.TYPING_PATTERNS[self.personality["typing_speed"]]
        wpm = self.rng.uniform(*pattern["wpm"])
        
        # Average person types ~5 chars per word
        chars_per_minute = wpm * 5
        delay_per_char = 60 / chars_per_minute
        
        sequence = []
        text_with_errors = self._add_typing_errors(text, pattern["error_rate"])
        
        for i, char in enumerate(text_with_errors):
            if char["action"] == "type":
                sequence.append({
                    "action": "keypress",
                    "key": char["char"],
                    "delay": delay_per_char * self.rng.uniform(0.5, 1.5),
                })
            elif char["action"] == "backspace":
                sequence.append({
                    "action": "backspace",
                    "delay": delay_per_char * self.rng.uniform(0.8, 1.2),
                })
            elif char["action"] == "pause":
                sequence.append({
                    "action": "pause",
                    "delay": self.rng.uniform(0.5, 2.0),
                })
        
        return sequence
    
    def _add_typing_errors(self, text: str, error_rate: float) -> List[Dict]:
        """Add realistic typing errors to text"""
        result = []
        
        # Common keyboard neighbors for errors
        keyboard_neighbors = {
            'ا': ['ي', 'ء'],
            'ب': ['ن', 'ت'],
            'ت': ['ب', 'ث'],
            'ث': ['ت', 'ج'],
            'ج': ['ث', 'ح'],
            'ح': ['ج', 'خ'],
            'خ': ['ح', 'د'],
            'a': ['s', 'q', 'z'],
            'b': ['v', 'n', 'g'],
            'c': ['x', 'v', 'f'],
            'd': ['s', 'e', 'f', 'x'],
            'e': ['w', 'r', 's', 'd'],
            'f': ['d', 'r', 'g', 'c'],
        }
        
        for char in text:
            if self.rng.random() < error_rate and char.lower() in keyboard_neighbors:
                # Make an error
                wrong_char = self.rng.choice(keyboard_neighbors[char.lower()])
                result.append({"action": "type", "char": wrong_char})
                result.append({"action": "pause", "delay": 0})
                result.append({"action": "backspace"})
                result.append({"action": "pause", "delay": 0})
            
            result.append({"action": "type", "char": char})
        
        return result
    
    def generate_scroll_sequence(self, page_height: int = 3000) -> List[Dict]:
        """Generate realistic scroll behavior"""
        pattern = self.SCROLL_PATTERNS[self.personality["scroll_style"]]
        
        sequence = []
        current_position = 0
        total_scrolls = self.rng.randint(*pattern["total"])
        
        for _ in range(total_scrolls):
            scroll_size = self.rng.randint(*pattern["scroll_size"])
            pause_time = self.rng.uniform(*pattern["pause"])
            
            # Sometimes scroll back up
            if self.rng.random() < 0.15:  # 15% chance to scroll up
                scroll_size = -scroll_size // 2
            
            current_position += scroll_size
            current_position = max(0, min(current_position, page_height))
            
            sequence.append({
                "action": "scroll",
                "delta": scroll_size,
                "position": current_position,
                "pause_after": pause_time,
            })
        
        return sequence
    
    def should_get_distracted(self) -> bool:
        """Determine if user gets distracted"""
        return self.rng.random() < self.personality["distraction_rate"]
    
    def get_distraction_action(self) -> str:
        """Get a distraction action"""
        distractions = [
            "switch_tab",
            "minimize_window",
            "check_phone",
            "look_away",
            "scroll_randomly",
            "open_new_tab",
        ]
        return self.rng.choice(distractions)
    
    def should_explore(self, current_context: str) -> bool:
        """Determine if user should explore something new"""
        return self.rng.random() < self.personality["curiosity_level"] * 0.3
    
    def get_exploration_target(self) -> str:
        """Get something to explore"""
        targets = [
            "click_suggested_post",
            "view_friend_profile",
            "browse_marketplace",
            "check_notifications",
            "view_group",
            "search_something",
            "watch_video",
        ]
        return self.rng.choice(targets)
    
    def get_natural_pause(self) -> float:
        """Get a natural pause duration"""
        if self.should_get_distracted():
            return self.rng.uniform(30, 180)  # 30s to 3min
        return self.rng.uniform(1, 10)
    
    def simulate_reading_time(self, text_length: int) -> float:
        """Simulate time to read text (in seconds)"""
        # Average reading speed: 200-300 words per minute
        # Assume ~5 chars per word in Arabic
        words = text_length / 5
        wpm = self.rng.uniform(150, 300) * self.personality["attention_span"]
        minutes = words / wpm
        return minutes * 60
    
    def record_action(self, action_type: str, details: Optional[Dict] = None):
        """Record an action for pattern analysis"""
        self.action_count += 1
        self.session_history.append({
            "type": action_type,
            "timestamp": datetime.now(),
            "details": details or {},
            "action_number": self.action_count,
        })
    
    def get_session_stats(self) -> Dict:
        """Get statistics about current session"""
        if not self.session_history:
            return {"actions": 0, "duration": 0}
        
        first = self.session_history[0]["timestamp"]
        last = self.session_history[-1]["timestamp"]
        duration = (last - first).total_seconds()
        
        return {
            "actions": len(self.session_history),
            "duration_seconds": duration,
            "avg_delay": duration / len(self.session_history) if self.session_history else 0,
        }
