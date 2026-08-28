"""
Account Generator - Creates realistic Algerian Facebook accounts
"""
import random
from typing import Dict, Optional
from datetime import datetime
from loguru import logger
from bot.config import BotConfig
from bot.utils import Utils


class AccountGenerator:
    """
    Generates realistic Facebook account profiles
    with Algerian names and details
    """
    
    def __init__(self):
        self.config = BotConfig
    
    def generate_account(self) -> Dict:
        """Generate a complete Facebook account profile"""
        gender = random.choice(["male", "female"])
        
        if gender == "male":
            first_name = random.choice(self.config.ALGERIAN_FIRST_NAMES_MALE)
        else:
            first_name = random.choice(self.config.ALGERIAN_FIRST_NAMES_FEMALE)
        
        last_name = random.choice(self.config.ALGERIAN_LAST_NAMES)
        display_name = f"{first_name} {last_name}"
        
        email = self._generate_email(first_name, last_name)
        password = Utils.generate_password(16)
        birth_date = Utils.generate_birth_date(min_age=22, max_age=45)
        city = random.choice(self.config.ALGERIAN_CITIES)
        profile_id = Utils.generate_profile_id()
        
        account = {
            "first_name": first_name,
            "last_name": last_name,
            "display_name": display_name,
            "gender": gender,
            "email": email,
            "password": password,
            "birth_date": birth_date,
            "city": city,
            "bio": self._generate_bio(gender, city),
            "profile_id": profile_id,
            "user_agent": self._get_user_agent(),
            "fingerprint_hash": Utils.generate_profile_id(),
            "created_at": datetime.now(),
        }
        
        logger.info(f"Generated account: {display_name} ({email})")
        return account
    
    def _generate_email(self, first_name: str, last_name: str) -> str:
        """Generate realistic email address"""
        domains = [
            "mailinator.com",
            "guerrillamail.com",
            "tempmail.com",
            "10minutemail.com",
            "yopmail.com",
            "temp-mail.org",
            "emailnax.com",
            "getnada.com",
        ]
        
        transliteration_map = {
            '\u0623': 'a', '\u0625': 'e', '\u0622': 'a',
            '\u0628': 'b', '\u062a': 't', '\u062b': 'th',
            '\u062c': 'j', '\u062d': 'h', '\u062e': 'kh',
            '\u062f': 'd', '\u0630': 'dh', '\u0631': 'r',
            '\u0632': 'z', '\u0633': 's', '\u0634': 'sh',
            '\u0635': 's', '\u0636': 'd', '\u0637': 't',
            '\u0638': 'z', '\u0639': 'a', '\u063a': 'gh',
            '\u0641': 'f', '\u0642': 'q', '\u0643': 'k',
            '\u0644': 'l', '\u0645': 'm', '\u0646': 'n',
            '\u0647': 'h', '\u0648': 'w', '\u064a': 'y',
            '\u0629': 'a', '\u0649': 'a', '\u0621': '',
            ' ': '_',
        }
        
        first_en = self._transliterate(first_name, transliteration_map)
        last_en = self._transliterate(last_name, transliteration_map)
        
        patterns = [
            f"{first_en}.{last_en}{random.randint(10, 99)}",
            f"{first_en}{last_en}{random.randint(100, 999)}",
            f"{first_en}_{last_en}",
            f"{first_en[0]}{last_en}{random.randint(1, 99)}",
            f"{first_en}{random.randint(1980, 2002)}",
        ]
        
        email_base = random.choice(patterns).lower()
        domain = random.choice(domains)
        
        return f"{email_base}@{domain}"
    
    def _transliterate(self, text: str, mapping: Dict) -> str:
        """Convert Arabic text to Latin characters"""
        result = []
        for char in text:
            if char in mapping:
                result.append(mapping[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def _generate_bio(self, gender: str, city: str) -> str:
        """Generate a realistic bio"""
        bios = [
            f"\u0645\u0646 {city} \u2764\ufe0f",
            f"\u0627\u0644\u062d\u0645\u062f \u0644\u0644\u0647 \u062f\u0627\u0626\u0645\u0627\u064b | {city}",
            "\u062d\u0633\u0627\u0628 \u0634\u062e\u0635\u064a",
            "\u2728 \u0627\u0644\u062d\u064a\u0627\u0629 \u062c\u0645\u064a\u0644\u0629 \u2728",
            f"{city} - \u0627\u0644\u062c\u0632\u0627\u0626\u0631",
            "\U0001f30d \u0645\u0633\u0627\u0641\u0631 \u0641\u064a \u0647\u0630\u0647 \u0627\u0644\u062d\u064a\u0627\u0629",
            "\U0001f4ab \u0635\u0627\u0646\u0639 \u0623\u062d\u0644\u0627\u0645\u064a",
            "\U0001f338 \u0627\u0644\u062d\u064a\u0627\u0629 \u0645\u0644\u064a\u0626\u0629 \u0628\u0627\u0644\u0641\u0631\u0635",
            f"\U0001f4cd {city}",
            "\u2615 \u0623\u062d\u0628 \u0627\u0644\u0642\u0647\u0648\u0629 \u0648\u0627\u0644\u0645\u0648\u0633\u064a\u0642\u0649",
            "\U0001f4da \u0645\u062d\u0628 \u0644\u0644\u0642\u0631\u0627\u0621\u0629",
            "\U0001f3c3 \u0631\u064a\u0627\u0636\u064a",
        ]
        return random.choice(bios)
    
    def _get_user_agent(self) -> str:
        """Get a realistic user agent string"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        ]
        return random.choice(agents)
    
    def generate_multiple_accounts(self, count: int) -> list:
        """Generate multiple accounts at once"""
        accounts = []
        for i in range(count):
            account = self.generate_account()
            accounts.append(account)
            logger.info(f"Generated account {i+1}/{count}: {account['display_name']}")
        return accounts
