"""
Bot Configuration v2.0
Enhanced configuration with all system settings
"""
import os
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    """Enhanced bot configuration settings"""
    
    # === General Settings ===
    BOT_ENABLED = os.getenv('BOT_ENABLED', 'true').lower() == 'true'
    BOT_INTERVAL_HOURS = int(os.getenv('BOT_INTERVAL_HOURS', '24'))
    MAX_ACCOUNTS_PER_DAY = int(os.getenv('MAX_ACCOUNTS_PER_DAY', '1'))
    BOT_MODE = os.getenv('BOT_MODE', 'safe')  # safe/balanced/aggressive
    
    # === Anti-Detection Settings v2 ===
    USE_PROXIES = os.getenv('USE_PROXIES', 'true').lower() == 'true'
    PROXY_ROTATION = os.getenv('PROXY_ROTATION', 'true').lower() == 'true'
    MIN_DELAY_SECONDS = int(os.getenv('MIN_DELAY_SECONDS', '30'))
    MAX_DELAY_SECONDS = int(os.getenv('MAX_DELAY_SECONDS', '120'))
    ENABLE_FINGERPRINTING = os.getenv('ENABLE_FINGERPRINTING', 'true').lower() == 'true'
    ENABLE_BEHAVIOR_SIM = os.getenv('ENABLE_BEHAVIOR_SIM', 'true').lower() == 'true'
    ANTI_PATTERN_DETECTION = os.getenv('ANTI_PATTERN_DETECTION', 'true').lower() == 'true'
    
    # === Account Settings ===
    DEFAULT_COUNTRY = os.getenv('DEFAULT_COUNTRY', 'DZ')
    GENERATE_REAL_PHOTOS = os.getenv('GENERATE_REAL_PHOTOS', 'true').lower() == 'true'
    ACCOUNT_MATURITY_DAYS = int(os.getenv('ACCOUNT_MATURITY_DAYS', '14'))
    MAX_ACCOUNT_AGE_DAYS = int(os.getenv('MAX_ACCOUNT_AGE_DAYS', '180'))
    
    # === Task Execution Settings ===
    MAX_RATINGS_PER_ACCOUNT = int(os.getenv('MAX_RATINGS_PER_ACCOUNT', '15'))
    RATING_INTERVAL_DAYS = int(os.getenv('RATING_INTERVAL_DAYS', '3'))
    MIN_STARS = int(os.getenv('MIN_STARS', '3'))
    MAX_STARS = int(os.getenv('MAX_STARS', '5'))
    COMMENTS_ENABLED = os.getenv('COMMENTS_ENABLED', 'true').lower() == 'true'
    
    # === Facebook URLs ===
    FACEBOOK_LOGIN_URL = os.getenv('FACEBOOK_LOGIN_URL', 'https://www.facebook.com/login')
    FACEBOOK_SIGNUP_URL = os.getenv('FACEBOOK_SIGNUP_URL', 'https://www.facebook.com/r.php')
    FACEBOOK_MOBILE_URL = os.getenv('FACEBOOK_MOBILE_URL', 'https://m.facebook.com')
    
    # === Backup Settings ===
    AUTO_BACKUP_ENABLED = os.getenv('AUTO_BACKUP_ENABLED', 'true').lower() == 'true'
    BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
    MAX_BACKUPS = int(os.getenv('MAX_BACKUPS', '7'))
    
    # === Notification Settings ===
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    # === Algerian Names Database ===
    ALGERIAN_FIRST_NAMES_MALE = [
        "محمد", "أحمد", "يوسف", "عبد الرحمن", "خالد", "عمر", "إبراهيم",
        "ياسين", "أيمن", "بلال", "رائد", "سامي", "كريم", "نور الدين",
        "أمين", "وليد", "زياد", "فادي", "حمزة", "إلياس", "ملاك",
        "سفيان", "ريان", "آدم", "إسماعيل", "طه", "عيسى", "شعيب",
        "إلياس", "أسامة", "طارق", "مراد", "نذير", "مهدي", "إبراهيم",
        "أنس", "بلال", "أيوب", "إلياس", "عبد الله", "جلال", "كمال",
    ]
    
    ALGERIAN_FIRST_NAMES_FEMALE = [
        "فاطمة", "عائشة", "مريم", "خديجة", "نور", "سارة", "ليلى",
        "ياسمين", "هدى", "رقية", "زينب", "آمنة", "حنان", "سلمى",
        "إيمان", "ريم", "دعاء", "أمل", "شيماء", "وفاء", "نسرين",
        "لينا", "ميساء", "تسنيم", "جنى", "إيناس", "رانيا", "هبة",
        "سعاد", "نادية", "أمينة", "فريدة", "حورية", "زهرة", "سامية",
        "عفاف", "سامية", "مليكة", "دليلة", "عزيزة", "صفية", "كريمة",
    ]
    
    ALGERIAN_LAST_NAMES = [
        "بن علي", "بوعلام", "حمداوي", "عبد الله", "بن عمر", "قاسمي",
        "بوزيد", "مرابط", "شريف", "بلحاج", "خليل", "مصطفاي", "حداد",
        "بن موسى", "طاهر", "بلعيد", "عبد الكريم", "بن سعيد", "فراج",
        "بن عيسى", "خليفي", "مدني", "بن ناصر", "حرابي", "سعيداني",
        "بن حميدة", "عبد النور", "براهيمي", "زياني", "عماري", "بلقاسم",
        "بن عمر", "مزيان", "بن عبد الله", "لعروسي", "بن سالم", "خضرة",
        "بوكرت", "حمروش", "شريف", "بن بوزيد", "مزاري", "بلعباس",
    ]
    
    ALGERIAN_CITIES = [
        "الجزائر العاصمة", "وهران", "قسنطينة", "عنابة", "سطيف",
        "باتنة", "تلمسان", "بجاية", "تيزي وزو", "البليدة",
        "البويرة", "جيجل", "سكيكدة", "المسيلة", "برج بوعريريج",
        "ورقلة", "غرداية", "تيارت", "معسكر", "سيدي بلعباس",
        "بشار", "الأغواط", "المدية", "بومرداس", "الطارف",
        "قالمة", "خنشلة", "أم البواقي", "سوق أهراس", "تبسة",
        "الشلف", "غليزان", "مستغانم", "عين الدفلى", "النعامة",
        "تيسمسيلت", "برج بوعريريج", "الوادي", "بسكرة", "المنيعة",
    ]
    
    # === Comment Templates (Arabic) ===
    POSITIVE_COMMENTS_5_STARS = [
        "منتج رائع جداً، أنصح به بشدة! 👍",
        "خدمة ممتازة وسرعة في التوصيل، شكراً لك!",
        "أفضل تجربة شراء، الجودة عالية والسعر مناسب",
        "تعامل راقي ومحترم، سأعود للشراء مرة أخرى",
        "منتج مطابق للوصف تماماً، راضٍ جداً",
        "بائع موثوق، المنتج وصل في الوقت المحدد",
        "جودة ممتازة، يستحق كل دينار",
        "تجربة رائعة، أنصح الجميع بالتعامل معه",
        "خدمة عملاء ممتازة ومنتج عالي الجودة",
        "أفضل متجر تعاملت معه، شكراً على الخدمة المميزة",
        "ماشاء الله، منتج ممتاز جداً!",
        "تبارك الرحمن، جودة خرافية 👏",
        "أنصح الكل بهذا المنتج، فعلاً رائع",
    ]
    
    POSITIVE_COMMENTS_4_STARS = [
        "منتج جيد جداً، أنصح به",
        "تجربة جيدة عموماً، شكراً",
        "الجودة مناسبة والسعر معقول",
        "سرعة في التوصيل، راضٍ عن المنتج",
        "خدمة جيدة، سأكرر التجربة",
        "منتج جيد ويستحق الشراء",
        "تعامل محترم ومنتج مطابق",
        "ممتاز لكن التوصيل تأخر قليلاً",
        "جيد جداً مع تحسينات بسيطة",
    ]
    
    POSITIVE_COMMENTS_3_STARS = [
        "المنتج لا بأس به",
        "جودة متوسطة لكن السعر مناسب",
        "تجربة عادية، لا سيء ولا ممتاز",
        "المنتج وصل بسلام، شكراً",
        "مقبول بالنسبة للسعر",
        "عادي لكن يفي بالغرض",
    ]
    
    SHORT_COMMENTS = [
        "ممتاز 👍",
        "رائع!",
        "شكراً لك",
        "خدمة جيدة",
        "أنصح به",
        "جودة عالية",
        "تجربة مميزة",
        "موثوق ✅",
        "بالتوفيق",
        "بارك الله فيك",
    ]
    
    # === Behavior Simulation Settings ===
    BROWSING_TIME_MIN = 180
    BROWSING_TIME_MAX = 600
    SCROLL_PAUSE_MIN = 2
    SCROLL_PAUSE_MAX = 8
    CLICK_DELAY_MIN = 1
    CLICK_DELAY_MAX = 5
    TYPING_SPEED_WPM = 35
    
    # === Human Error Simulation ===
    TYPO_PROBABILITY = 0.1
    CORRECTION_PROBABILITY = 0.7
    
    # === Session Settings ===
    SESSION_TIMEOUT_MIN = 900
    SESSION_TIMEOUT_MAX = 3600
    MAX_ACTIONS_PER_SESSION = 10
    
    # === Safety Levels ===
    SAFETY_LEVELS = {
        "safe": {
            "min_delay": 60,
            "max_delay": 300,
            "max_daily_accounts": 1,
            "max_ratings_per_day": 5,
            "maturity_days": 21,
        },
        "balanced": {
            "min_delay": 30,
            "max_delay": 120,
            "max_daily_accounts": 2,
            "max_ratings_per_day": 10,
            "maturity_days": 14,
        },
        "aggressive": {
            "min_delay": 15,
            "max_delay": 60,
            "max_daily_accounts": 3,
            "max_ratings_per_day": 20,
            "maturity_days": 7,
        },
    }
    
    @classmethod
    def get_safety_config(cls):
        """Get configuration based on safety level"""
        return cls.SAFETY_LEVELS.get(cls.BOT_MODE, cls.SAFETY_LEVELS["safe"])
    
    @classmethod
    def get_comment_for_stars(cls, stars):
        """Get a random comment based on star rating"""
        import random
        
        if stars == 5:
            return random.choice(cls.POSITIVE_COMMENTS_5_STARS)
        elif stars == 4:
            return random.choice(cls.POSITIVE_COMMENTS_4_STARS)
        elif stars == 3:
            return random.choice(cls.POSITIVE_COMMENTS_3_STARS)
        else:
            return random.choice(cls.SHORT_COMMENTS)
    
    @classmethod
    def get_random_comment(cls):
        """Get a completely random comment"""
        import random
        all_comments = (
            cls.POSITIVE_COMMENTS_5_STARS +
            cls.POSITIVE_COMMENTS_4_STARS +
            cls.POSITIVE_COMMENTS_3_STARS +
            cls.SHORT_COMMENTS
        )
        return random.choice(all_comments)
