"""
Device Fingerprinting Agent - Detects device-based fraud
Self-contained: Uses device info from transaction headers
Detects: Device spoofing, emulator usage, device sharing
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from .base_agent import BaseFraudAgent, RiskAssessment
import hashlib


class DeviceFingerprintAgent(BaseFraudAgent):
    """
    Agent for device fingerprinting and device-based fraud detection
    """
    
    def __init__(self):
        super().__init__(
            name="device_fingerprint",
            description="Detecao de fraude baseada em dispositivo - spoofing, emuladores, partilha",
            version="1.0"
        )
        self.device_history = defaultdict(list)  # customer_id -> list of devices
        self.known_devices = {}  # device_id -> customer_id mapping
        
    def evaluate(self, transaction: Dict[str, Any], context: Dict = None) -> RiskAssessment:
        """Evaluate device fingerprint for fraud indicators"""
        start_time = datetime.now()
        flags = []
        score = 0.0
        explanations = []
        
        customer_id = transaction.get("customer_id")
        device_info = transaction.get("device_info", {})
        
        if not device_info:
            return self._create_neutral_assessment("No device info provided")
        
        # Generate device fingerprint
        device_fingerprint = self._generate_fingerprint(device_info)
        
        # Check 1: Device sharing (same device, multiple accounts)
        sharing_score, sharing_flags = self._check_device_sharing(
            device_fingerprint, customer_id
        )
        score += sharing_score
        flags.extend(sharing_flags)
        if sharing_flags:
            explanations.append("Device sharing detected")
        
        # Check 2: Rapid device changes
        rapid_score, rapid_flags = self._check_rapid_device_changes(customer_id, device_fingerprint)
        score += rapid_score
        flags.extend(rapid_flags)
        if rapid_flags:
            explanations.append("Rapid device switching")
        
        # Check 3: Emulator/VM detection
        emulator_score, emulator_flags = self._detect_emulator(device_info)
        score += emulator_score
        flags.extend(emulator_flags)
        if emulator_flags:
            explanations.append("Virtual machine/emulator detected")
        
        # Check 4: Browser consistency
        browser_score, browser_flags = self._check_browser_consistency(device_info)
        score += browser_score
        flags.extend(browser_flags)
        if browser_flags:
            explanations.append("Browser anomalies detected")
        
        # Check 5: Screen/Resolution anomalies
        screen_score, screen_flags = self._check_screen_anomalies(device_info)
        score += screen_score
        flags.extend(screen_flags)
        if screen_flags:
            explanations.append("Screen resolution anomalies")
        
        # Store device info
        self._store_device_info(customer_id, device_fingerprint, device_info)
        
        score = min(score, 100)
        
        if score >= 70:
            action = "BLOCK"
        elif score >= 40:
            action = "REVIEW"
        else:
            action = "APPROVE"
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        self.update_metrics(processing_time)
        
        return RiskAssessment(
            score=score,
            confidence=0.85 if flags else 0.6,
            flags=list(set(flags)),
            explanation="; ".join(explanations) if explanations else f"Device normal (score: {score:.1f})",
            recommended_action=action,
            timestamp=datetime.now(),
            agent_name=self.name
        )
    
    def _generate_fingerprint(self, device_info: Dict) -> str:
        """Generate unique device fingerprint"""
        components = [
            device_info.get("user_agent", ""),
            device_info.get("screen_resolution", ""),
            device_info.get("color_depth", ""),
            device_info.get("timezone", ""),
            device_info.get("language", ""),
            device_info.get("platform", ""),
            device_info.get("touch_support", ""),
        ]
        fingerprint_data = "|".join(components)
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
    
    def _check_device_sharing(self, device_fingerprint: str, customer_id: str) -> tuple:
        """Check if device is shared among multiple accounts"""
        score = 0.0
        flags = []
        
        if device_fingerprint in self.known_devices:
            known_customer = self.known_devices[device_fingerprint]
            if known_customer != customer_id:
                # Device used by different customer!
                score += 35
                flags.append("DEVICE_SHARING: Same device used by multiple accounts")
        else:
            # First time seeing this device
            self.known_devices[device_fingerprint] = customer_id
        
        return score, flags
    
    def _check_rapid_device_changes(self, customer_id: str, current_device: str) -> tuple:
        """Check if customer is rapidly switching devices"""
        score = 0.0
        flags = []
        
        if customer_id not in self.device_history:
            return score, flags
        
        history = self.device_history[customer_id]
        if len(history) < 2:
            return score, flags
        
        # Check last 24 hours
        recent_devices = [
            h for h in history 
            if (datetime.now() - h["timestamp"]).total_seconds() < 86400
        ]
        
        unique_devices = len(set(h["fingerprint"] for h in recent_devices))
        
        if unique_devices >= 5:
            score += 30
            flags.append(f"RAPID_DEVICE_CHANGE: {unique_devices} different devices in 24h")
        elif unique_devices >= 3:
            score += 15
            flags.append(f"MULTIPLE_DEVICES: {unique_devices} devices in 24h")
        
        return score, flags
    
    def _detect_emulator(self, device_info: Dict) -> tuple:
        """Detect if device is an emulator or VM"""
        score = 0.0
        flags = []
        
        user_agent = device_info.get("user_agent", "").lower()
        platform = device_info.get("platform", "").lower()
        
        # Emulator indicators
        emulator_indicators = [
            "emulator", "simulator", "virtual", "vmware", "virtualbox",
            "qemu", "xen", "parallels", "hyper-v"
        ]
        
        for indicator in emulator_indicators:
            if indicator in user_agent or indicator in platform:
                score += 40
                flags.append(f"EMULATOR_DETECTED: {indicator}")
                break
        
        # Screen resolution checks (emulators often have standard resolutions)
        resolution = device_info.get("screen_resolution", "")
        if resolution in ["1920x1080", "1366x768"] and "mobile" in user_agent:
            # Desktop resolution on mobile UA
            score += 15
            flags.append("RESOLUTION_MISMATCH: Desktop resolution on mobile device")
        
        return score, flags
    
    def _check_browser_consistency(self, device_info: Dict) -> tuple:
        """Check for browser inconsistencies"""
        score = 0.0
        flags = []
        
        user_agent = device_info.get("user_agent", "")
        
        # Check for headless browsers (often used in automation)
        headless_indicators = ["headlesschrome", "phantomjs", "sel