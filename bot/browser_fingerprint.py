"""
Advanced Browser Fingerprint Management
Makes each bot session look like a unique real browser
"""
import random
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime


class BrowserFingerprint:
    """
    Advanced browser fingerprint generator
    Creates unique, consistent fingerprints for each session
    """
    
    # Screen resolutions (common)
    SCREEN_RESOLUTIONS = [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1280, 720), (1600, 900), (1280, 800), (1024, 768),
        (2560, 1440), (1680, 1050), (1920, 1200), (1360, 768),
    ]
    
    # Color depths
    COLOR_DEPTHS = [24, 32]
    
    # Pixel ratios
    PIXEL_RATIOS = [1, 1.25, 1.5, 2]
    
    # Timezones (realistic)
    TIMEZONES = [
        "Africa/Algiers",
        "Africa/Tunis",
        "Africa/Casablanca",
        "Europe/Paris",
        "Europe/London",
    ]
    
    # Languages
    LANGUAGES = [
        ["ar-DZ", "ar", "fr"],
        ["ar", "fr"],
        ["ar-DZ", "fr-FR"],
        ["ar", "en-US", "en"],
    ]
    
    # WebGL Vendors
    WEBGL_VENDORS = [
        "Google Inc. (NVIDIA Corporation)",
        "Google Inc. (Intel Inc.)",
        "Google Inc. (AMD)",
        "Google Inc. (NVIDIA Corporation) -- OpenGL ES 3.0 NVIDIA",
        "Google Inc. (Intel Inc.) -- OpenGL ES 3.0 (Intel(R) UHD Graphics)",
    ]
    
    WEBGL_RENDERERS = [
        "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0)",
    ]
    
    # Audio fingerprints
    AUDIO_CONTEXTS = [
        {"sampleRate": 44100, "channelCount": 2, "maxChannelCount": 32},
        {"sampleRate": 48000, "channelCount": 2, "maxChannelCount": 32},
        {"sampleRate": 44100, "channelCount": 2, "maxChannelCount": 2},
    ]
    
    # Font lists (realistic sets)
    FONT_SETS = [
        ["Arial", "Verdana", "Helvetica", "Times New Roman", "Courier New", "Georgia", "Tahoma", "Segoe UI"],
        ["Arial", "Calibri", "Cambria", "Times New Roman", "Segoe UI", "Consolas", "Trebuchet MS"],
        ["Helvetica Neue", "San Francisco", "Lucida Grande", "Menlo", "Monaco"],
    ]
    
    # Canvas noise patterns
    CANVAS_HASHES = [
        "a8f3c2b1d4e5f678",
        "b7e6d5c4a3f2e190",
        "c9d8e7f6a5b4c3d2",
        "d1e2f3a4b5c6d7e8",
        "e5f6a7b8c9d0e1f2",
    ]
    
    def __init__(self, seed: Optional[str] = None):
        self.seed = seed or str(datetime.now().timestamp())
        self._rng = random.Random(hashlib.md5(self.seed.encode()).hexdigest())
        self.fingerprint = self._generate()
    
    def _generate(self) -> Dict:
        """Generate complete browser fingerprint"""
        # Screen
        resolution = self._rng.choice(self.SCREEN_RESOLUTIONS)
        
        # Fonts
        font_set = self._rng.choice(self.FONT_SETS)
        font_count = self._rng.randint(len(font_set) - 3, len(font_set))
        fonts = self._rng.sample(font_set, font_count)
        
        fingerprint = {
            "screen": {
                "width": resolution[0],
                "height": resolution[1],
                "availWidth": resolution[0],
                "availHeight": resolution[1] - self._rng.choice([30, 40, 48, 60, 72]),
                "colorDepth": self._rng.choice(self.COLOR_DEPTHS),
                "pixelDepth": self._rng.choice(self.COLOR_DEPTHS),
                "pixelRatio": self._rng.choice(self.PIXEL_RATIOS),
            },
            "navigator": {
                "hardwareConcurrency": self._rng.choice([2, 4, 6, 8, 12, 16]),
                "deviceMemory": self._rng.choice([2, 4, 8, 16]),
                "maxTouchPoints": 0,  # Desktop
                "platform": self._rng.choice(["Win32", "MacIntel", "Linux x86_64"]),
                "vendor": "Google Inc.",
                "language": "ar-DZ",
                "languages": self._rng.choice(self.LANGUAGES),
            },
            "webgl": {
                "vendor": self._rng.choice(self.WEBGL_VENDORS),
                "renderer": self._rng.choice(self.WEBGL_RENDERERS),
            },
            "audio": self._rng.choice(self.AUDIO_CONTEXTS),
            "fonts": fonts,
            "canvas": self._rng.choice(self.CANVAS_HASHES),
            "timezone": self._rng.choice(self.TIMEZONES),
            "do_not_track": self._rng.choice([None, "1", "0"]),
            "plugins": self._generate_plugins(),
            "mime_types": self._generate_mime_types(),
        }
        
        return fingerprint
    
    def _generate_plugins(self) -> List[Dict]:
        """Generate realistic browser plugins"""
        plugin_sets = [
            [
                {"name": "PDF Viewer", "filename": "internal-pdf-viewer"},
                {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer"},
                {"name": "Chromium PDF Viewer", "filename": "internal-pdf-viewer"},
                {"name": "Microsoft Edge PDF Viewer", "filename": "internal-pdf-viewer"},
                {"name": "WebKit built-in PDF", "filename": "internal-pdf-viewer"},
            ],
            [
                {"name": "PDF Viewer", "filename": "internal-pdf-viewer"},
                {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer"},
            ],
            [],  # Some users have no plugins
        ]
        return self._rng.choice(plugin_sets)
    
    def _generate_mime_types(self) -> List[str]:
        """Generate realistic MIME types"""
        base_types = [
            "application/pdf",
            "application/x-google-chrome-pdf",
            "application/x-nacl",
            "application/x-pnacl",
            "application/xhtml+xml",
            "application/xml",
            "application/json",
            "text/html",
            "text/plain",
            "text/xml",
            "image/png",
            "image/jpeg",
            "image/gif",
            "image/webp",
        ]
        count = self._rng.randint(5, len(base_types))
        return self._rng.sample(base_types, count)
    
    def get_stealth_script(self) -> str:
        """Generate JavaScript to inject for stealth"""
        fp = self.fingerprint
        
        return f"""
            // Override navigator properties
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {fp['navigator']['hardwareConcurrency']}
            }});
            
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {fp['navigator']['deviceMemory']}
            }});
            
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{fp['navigator']['platform']}'
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: () => {json.dumps(fp['navigator']['languages'])}
            }});
            
            Object.defineProperty(navigator, 'plugins', {{
                get: () => {{
                    const plugins = {json.dumps(fp['plugins'])};
                    return {{
                        length: plugins.length,
                        item: (i) => plugins[i],
                        namedItem: (name) => plugins.find(p => p.name === name),
                        refresh: () => {{}},
                        [Symbol.iterator]: function*() {{ yield* plugins; }}
                    }};
                }}
            }});
            
            // Override screen properties
            Object.defineProperty(screen, 'width', {{
                get: () => {fp['screen']['width']}
            }});
            
            Object.defineProperty(screen, 'height', {{
                get: () => {fp['screen']['height']}
            }});
            
            Object.defineProperty(screen, 'availWidth', {{
                get: () => {fp['screen']['availWidth']}
            }});
            
            Object.defineProperty(screen, 'availHeight', {{
                get: () => {fp['screen']['availHeight']}
            }});
            
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {fp['screen']['colorDepth']}
            }});
            
            // WebGL override
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(param) {{
                if (param === 37445) return '{fp['webgl']['vendor']}';
                if (param === 37446) return '{fp['webgl']['renderer']}';
                return getParameter.call(this, param);
            }};
            
            // Remove automation indicators
            delete window.cdc_ado_QpoTUQ;
            delete window.cdc_ado_SelfTest;
            delete window.cdc_ado_cXklyv;
            
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => false
            }});
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({{ state: Notification.permission }}) :
                    originalQuery(parameters)
            );
            
            // Canvas fingerprint noise
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                const ctx = this.getContext('2d');
                if (ctx) {{
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {{
                        imageData.data[i] += Math.floor(Math.random() * 2);
                    }}
                    ctx.putImageData(imageData, 0, 0);
                }}
                return originalToDataURL.call(this, type);
            }};
            
            // AudioContext noise
            const originalCreateOscillator = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {{
                const oscillator = originalCreateOscillator.call(this);
                return oscillator;
            }};
            
            // Override connection type
            Object.defineProperty(navigator, 'connection', {{
                get: () => ({{
                    effectiveType: '{self._rng.choice(['4g', '3g'])}',
                    rtt: {self._rng.randint(50, 200)},
                    downlink: {round(self._rng.uniform(1.5, 10), 1)},
                    saveData: false
                }})
            }});
            
            console.log('[Stealth] Fingerprint injected successfully');
        """
    
    def get_hash(self) -> str:
        """Get fingerprint hash for tracking"""
        fp_str = json.dumps(self.fingerprint, sort_keys=True)
        return hashlib.md5(fp_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Return fingerprint as dictionary"""
        return self.fingerprint
