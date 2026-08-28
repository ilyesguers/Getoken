"""
Proxy Manager - Fetches and manages free proxies
"""
import random
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

from database import SessionLocal, Proxy


class ProxyManager:
    """Manages free proxy rotation and validation"""
    
    FREE_PROXY_SOURCES = [
        "https://www.sslproxies.org/",
        "https://free-proxy-list.net/",
        "https://www.us-proxy.org/",
    ]
    
    def __init__(self):
        self.proxies: List[Dict] = []
        self.current_proxy_index = 0
    
    def fetch_free_proxies(self) -> List[Dict]:
        """Fetch free proxies from public sources"""
        proxies = []
        
        try:
            # Fetch from multiple sources
            for source in self.FREE_PROXY_SOURCES:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        # Parse proxy list (simplified)
                        # In production, use BeautifulSoup to parse actual HTML
                        logger.info(f"Fetched proxies from {source}")
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
            
            # Fallback: use some known free proxies
            fallback_proxies = [
                {"address": "103.152.112.162", "port": 80, "proxy_type": "http"},
                {"address": "103.152.112.120", "port": 80, "proxy_type": "http"},
                {"address": "191.241.162.42", "port": 999, "proxy_type": "http"},
                {"address": "103.152.112.112", "port": 80, "proxy_type": "http"},
            ]
            
            proxies.extend(fallback_proxies)
            
        except Exception as e:
            logger.error(f"Error fetching proxies: {e}")
        
        return proxies
    
    def validate_proxy(self, proxy: Dict) -> bool:
        """Test if a proxy is working"""
        try:
            proxy_url = f"{proxy['proxy_type']}://{proxy['address']}:{proxy['port']}"
            
            response = requests.get(
                "https://httpbin.org/ip",
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_working_proxies(self) -> List[Dict]:
        """Get list of working proxies"""
        all_proxies = self.fetch_free_proxies()
        working = []
        
        for proxy in all_proxies:
            if self.validate_proxy(proxy):
                working.append(proxy)
                logger.info(f"Working proxy found: {proxy['address']}:{proxy['port']}")
            
            # Don't test too many at once
            if len(working) >= 5:
                break
        
        self.proxies = working
        return working
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy in rotation"""
        if not self.proxies:
            self.get_working_proxies()
        
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return proxy
    
    def save_proxy_to_db(self, proxy: Dict):
        """Save proxy to database"""
        db = SessionLocal()
        try:
            existing = db.query(Proxy).filter(
                Proxy.address == proxy['address'],
                Proxy.port == proxy['port']
            ).first()
            
            if existing:
                existing.times_used += 1
                existing.last_used = datetime.now()
            else:
                new_proxy = Proxy(
                    address=proxy['address'],
                    port=proxy['port'],
                    proxy_type=proxy.get('proxy_type', 'http'),
                    times_used=1,
                    last_used=datetime.now(),
                )
                db.add(new_proxy)
            
            db.commit()
        except Exception as e:
            logger.error(f"Error saving proxy: {e}")
        finally:
            db.close()
    
    def get_proxies_from_db(self) -> List[Dict]:
        """Get proxies from database"""
        db = SessionLocal()
        try:
            proxies = db.query(Proxy).filter(
                Proxy.is_active == True,
                Proxy.is_working == True
            ).all()
            
            return [
                {
                    "address": p.address,
                    "port": p.port,
                    "proxy_type": p.proxy_type,
                }
                for p in proxies
            ]
        finally:
            db.close()
