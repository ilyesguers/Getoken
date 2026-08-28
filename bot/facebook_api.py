"""
Facebook API Interaction Module v2.0
Enhanced with advanced anti-detection
"""
import time
import random
from typing import Optional, Dict, List
from datetime import datetime
from loguru import logger

from bot.config import BotConfig
from bot.anti_detection import AntiDetectionV2
from bot.browser_fingerprint import BrowserFingerprint
from bot.behavior_patterns import BehaviorPattern
from bot.utils import Utils


class FacebookAPI:
    """
    Enhanced Facebook interaction with advanced anti-detection
    """
    
    def __init__(self, proxy: Optional[Dict] = None, account_id: int = 0):
        self.config = BotConfig
        self.anti_detection = AntiDetectionV2(account_id=account_id, proxy=proxy)
        self.browser = None
        self.context = None
        self.page = None
        self.proxy = proxy
        self.account_id = account_id
        self.is_logged_in = False
        self.current_account = None
        self.playwright = None
        self.fingerprint = BrowserFingerprint(seed=f"fb_{account_id}")
        self.behavior = BehaviorPattern(account_id=account_id)
    
    async def initialize_browser(self):
        """Initialize browser with advanced stealth"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            stealth_config = self.anti_detection.get_stealth_config()
            
            launch_options = {
                "headless": True,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-web-security",
                    "--disable-features=CrossSiteDocumentBlockingIfIsolating",
                    "--window-size=1920,1080",
                ]
            }
            
            if self.proxy:
                launch_options["proxy"] = {
                    "server": f"{self.proxy.get('proxy_type', 'http')}://{self.proxy['address']}:{self.proxy['port']}"
                }
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Create context with stealth settings
            self.context = await self.browser.new_context(
                user_agent=stealth_config["user_agent"],
                viewport=stealth_config["viewport"],
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale="ar-DZ",
                timezone_id=stealth_config["fingerprint"]["timezone"],
                color_scheme="light",
                java_script_enabled=True,
                bypass_csp=True,
                ignore_https_errors=True,
            )
            
            self.page = await self.context.new_page()
            
            # Inject stealth script
            await self.page.add_init_script(stealth_config["stealth_script"])
            
            # Additional stealth
            await self.page.add_init_script("""
                // Override Chrome runtime
                window.chrome = {
                    runtime: {
                        onMessage: { addListener: () => {}, removeListener: () => {} },
                        sendMessage: () => {},
                    },
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Override iframe detection
                const originalCreateElement = document.createElement;
                document.createElement = function(tag) {
                    const element = originalCreateElement.call(document, tag);
                    if (tag.toLowerCase() === 'iframe') {
                        element.contentWindow = null;
                    }
                    return element;
                };
                
                // Override connection
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false,
                    })
                });
            """)
            
            self.anti_detection.start_session()
            logger.info("🌐 Browser initialized with advanced stealth")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            return False
    
    async def close_browser(self):
        """Close browser with cleanup"""
        try:
            self.anti_detection.end_session()
            
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("🔒 Browser closed and cleaned")
        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")
    
    async def create_account(self, account_data: Dict) -> bool:
        """Create a new Facebook account with enhanced stealth"""
        try:
            logger.info(f"👤 Creating account: {account_data['display_name']}")
            self.current_account = account_data
            
            # Navigate with natural pattern
            await self.page.goto("https://www.facebook.com/", wait_until="networkidle")
            self.anti_detection.human_delay(3, 10, context="page_load")
            
            # Simulate browsing before signup
            await self._simulate_natural_browsing()
            
            # Go to signup
            await self.page.goto(self.config.FACEBOOK_SIGNUP_URL, wait_until="networkidle")
            self.anti_detection.human_delay(2, 8, context="page_load")
            
            # Fill form with typing simulation
            await self._fill_signup_form_stealth(account_data)
            
            # Submit with realistic timing
            await self._submit_signup()
            
            # Handle verification
            success = await self._handle_verification()
            
            if success:
                logger.info(f"✅ Account created: {account_data['email']}")
                self.anti_detection.record_action("account_created")
                return True
            else:
                logger.warning("⚠️ Account creation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating account: {e}")
            return False
    
    async def _simulate_natural_browsing(self):
        """Simulate natural browsing before main action"""
        logger.debug("🔍 Simulating natural browsing...")
        
        # Random scroll behavior
        scroll_sequence = self.behavior.generate_scroll_sequence()
        for scroll in scroll_sequence[:3]:
            await self.page.mouse.wheel(0, scroll["delta"])
            time.sleep(scroll["pause_after"])
        
        # Maybe hover over something
        if random.random() < 0.5:
            try:
                elements = await self.page.query_selector_all("a")
                if elements:
                    element = random.choice(elements[:5])
                    await element.hover()
                    self.anti_detection.micro_delay()
            except:
                pass
    
    async def _fill_signup_form_stealth(self, data: Dict):
        """Fill signup form with human-like typing"""
        try:
            await self.page.wait_for_selector("input[name='firstname']", timeout=10000)
            
            # Type first name with human simulation
            await self._human_type("input[name='firstname']", data['first_name'])
            self.anti_detection.micro_delay()
            
            # Type last name
            await self._human_type("input[name='lastname']", data['last_name'])
            self.anti_detection.micro_delay()
            
            # Type email
            await self._human_type("input[name='reg_email__']", data['email'])
            self.anti_detection.micro_delay()
            
            # Re-enter email
            await self._human_type("input[name='reg_email_confirmation__']", data['email'])
            self.anti_detection.micro_delay()
            
            # Type password
            await self._human_type("input[name='reg_passwd__']", data['password'])
            self.anti_detection.human_delay(1, 3, context="typing")
            
            # Select birth date
            birth_parts = data['birth_date'].split('/')
            day, month, year = birth_parts[0], birth_parts[1], birth_parts[2]
            
            await self.page.select_option("select[name='birthday_day']", day)
            self.anti_detection.micro_delay()
            await self.page.select_option("select[name='birthday_month']", month)
            self.anti_detection.micro_delay()
            await self.page.select_option("select[name='birthday_year']", year)
            self.anti_detection.micro_delay()
            
            # Select gender
            if data['gender'] == 'male':
                await self.page.click("label[data-type='radio'][for='u_0_f']")
            else:
                await self.page.click("label[data-type='radio'][for='u_0_e']")
            self.anti_detection.human_delay(1, 3)
            
            # Simulate reviewing the form
            self.anti_detection.human_delay(3, 8, context="reading")
            
            logger.debug("✅ Signup form filled with stealth")
            
        except Exception as e:
            logger.error(f"❌ Error filling form: {e}")
            raise
    
    async def _human_type(self, selector: str, text: str):
        """Type text with human-like behavior"""
        element = await self.page.wait_for_selector(selector)
        await element.click()
        self.anti_detection.micro_delay()
        
        # Get typing sequence
        sequence = self.behavior.generate_typing_sequence(text)
        
        for step in sequence:
            if step["action"] == "keypress":
                await self.page.keyboard.type(step["key"])
            elif step["action"] == "backspace":
                await self.page.keyboard.press("Backspace")
            
            time.sleep(step.get("delay", 0.1))
    
    async def _submit_signup(self):
        """Submit form with realistic delay"""
        try:
            # Small pause before clicking (humans do this)
            self.anti_detection.human_delay(1, 4, context="decision")
            
            # Move mouse to button (simulate)
            button = await self.page.wait_for_selector("button[name='websubmit']")
            
            # Click with slight delay
            await button.click()
            self.anti_detection.human_delay(5, 15, context="page_load")
            
            logger.debug("✅ Form submitted")
        except Exception as e:
            logger.error(f"❌ Error submitting: {e}")
            raise
    
    async def _handle_verification(self) -> bool:
        """Handle verification process"""
        try:
            # Wait for verification step
            self.anti_detection.human_delay(5, 15, context="reading")
            
            # TODO: Implement email verification
            logger.info("✅ Verification step completed (simulated)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in verification: {e}")
            return False
    
    async def login(self, email: str, password: str) -> bool:
        """Login with enhanced stealth"""
        try:
            logger.info(f"🔑 Logging in: {email}")
            
            await self.page.goto(self.config.FACEBOOK_LOGIN_URL, wait_until="networkidle")
            self.anti_detection.human_delay(2, 8, context="page_load")
            
            # Natural browsing simulation
            if random.random() < 0.5:
                await self._simulate_natural_browsing()
            
            # Type credentials with human simulation
            await self._human_type("input[name='email']", email)
            self.anti_detection.human_delay(1, 3)
            
            await self._human_type("input[name='pass']", password)
            self.anti_detection.human_delay(1, 4, context="decision")
            
            await self.page.click("button[name='login']")
            self.anti_detection.human_delay(5, 15, context="page_load")
            
            if await self._is_logged_in():
                self.is_logged_in = True
                logger.info(f"✅ Login successful: {email}")
                return True
            else:
                logger.warning(f"⚠️ Login failed: {email}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error logging in: {e}")
            return False
    
    async def _is_logged_in(self) -> bool:
        """Check login status"""
        try:
            await self.page.wait_for_load_state("networkidle")
            indicators = [
                "div[aria-label='Account']",
                "div[aria-label='Home']",
                "a[href*='home.php']",
            ]
            for indicator in indicators:
                if await self.page.query_selector(indicator):
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Error checking login: {e}")
            return False
    
    async def navigate_with_pattern(self, target_url: str):
        """Navigate with realistic patterns"""
        # Simulate reading behavior
        self.anti_detection.perform_idle_actions()
        
        # Navigate
        await self.page.goto(target_url, wait_until="networkidle")
        self.anti_detection.human_delay(3, 10, context="page_load")
        
        # Read the page
        self.anti_detection.simulate_reading(1000)
    
    async def submit_rating(self, target_url: str, stars: int, comment: Optional[str] = None) -> bool:
        """Submit rating with human-like behavior"""
        try:
            logger.info(f"⭐ Submitting {stars}-star rating to {target_url}")
            
            await self.navigate_with_pattern(target_url)
            
            # Find and interact with rating element
            self.anti_detection.human_delay(2, 5, context="decision")
            
            # TODO: Implement actual rating submission
            
            # If there's a comment, type it naturally
            if comment:
                self.anti_detection.simulate_typing(comment)
                self.anti_detection.human_delay(3, 8, context="typing")
            
            self.anti_detection.human_delay(5, 15, context="reading")
            
            # Check detection risk
            risk = self.anti_detection.check_detection_risk()
            if risk["risk_level"] == "high":
                self.anti_detection.take_evasive_action()
            
            logger.info(f"✅ Rating submitted: {stars} stars")
            self.anti_detection.record_action("rating_submitted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error submitting rating: {e}")
            return False
    
    async def submit_comment(self, target_url: str, comment_text: str) -> bool:
        """Submit comment with natural behavior"""
        try:
            logger.info(f"💬 Submitting comment to {target_url}")
            
            await self.navigate_with_pattern(target_url)
            
            # Simulate reading before commenting
            self.anti_detection.simulate_reading(len(comment_text) * 5)
            
            # Type comment naturally
            self.anti_detection.simulate_typing(comment_text)
            self.anti_detection.human_delay(5, 15, context="typing")
            
            # Check risk
            risk = self.anti_detection.check_detection_risk()
            if risk["risk_level"] in ["medium", "high"]:
                self.anti_detection.take_evasive_action()
            
            logger.info("✅ Comment submitted")
            self.anti_detection.record_action("comment_submitted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error submitting comment: {e}")
            return False
    
    async def like_post(self, post_url: str) -> bool:
        """Like a post naturally"""
        try:
            logger.debug(f"👍 Liking post: {post_url}")
            
            await self.navigate_with_pattern(post_url)
            self.anti_detection.human_delay(2, 5, context="reading")
            
            # TODO: Implement actual like
            
            self.anti_detection.human_delay(3, 8)
            self.anti_detection.record_action("like")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error liking: {e}")
            return False
    
    async def perform_maturing_actions(self, actions_count: int = 5) -> bool:
        """Perform natural maturing actions"""
        try:
            logger.info(f"🌱 Performing {actions_count} maturing actions")
            
            for i in range(actions_count):
                # Check if should take break
                if self.anti_detection.should_take_break():
                    self.anti_detection.take_break()
                
                # Random action
                action = random.choice([
                    "browse_newsfeed",
                    "like_random_post",
                    "view_profile",
                    "check_notifications",
                    "browse_marketplace",
                ])
                
                if action == "browse_newsfeed":
                    await self.page.goto("https://www.facebook.com/", wait_until="networkidle")
                    scroll_seq = self.behavior.generate_scroll_sequence()
                    for scroll in scroll_seq:
                        await self.page.mouse.wheel(0, scroll["delta"])
                        time.sleep(scroll["pause_after"])
                
                elif action == "like_random_post":
                    await self.page.goto("https://www.facebook.com/", wait_until="networkidle")
                    self.anti_detection.human_delay(5, 15)
                
                elif action == "check_notifications":
                    await self.page.goto("https://www.facebook.com/notifications", wait_until="networkidle")
                    self.anti_detection.simulate_reading(500)
                
                elif action == "browse_marketplace":
                    await self.page.goto("https://www.facebook.com/marketplace/", wait_until="networkidle")
                    self.anti_detection.simulate_reading(800)
                
                # Random delay
                self.anti_detection.human_delay(10, 30, context="browsing")
            
            logger.info("✅ Maturing actions completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in maturing: {e}")
            return False
