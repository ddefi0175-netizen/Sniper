"""
Notification Service - Multi-channel alerts and notifications.

Supports Telegram, Discord, Email, and webhook notifications.
"""

import logging
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
import json

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Available notification channels."""
    TELEGRAM = "telegram"
    DISCORD = "discord"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationConfig:
    """Configuration for notification service."""
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Discord
    discord_webhook_url: Optional[str] = None
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    email_to: Optional[List[str]] = None
    
    # Webhooks
    webhook_urls: List[str] = field(default_factory=list)
    
    # Settings
    enabled_channels: List[NotificationChannel] = field(default_factory=list)
    min_priority: NotificationPriority = NotificationPriority.NORMAL
    
    @classmethod
    def from_env(cls) -> "NotificationConfig":
        """Load configuration from environment variables."""
        return cls(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
            email_from=os.getenv("EMAIL_FROM"),
            email_to=os.getenv("EMAIL_TO", "").split(",") if os.getenv("EMAIL_TO") else None,
        )


@dataclass
class NotificationResult:
    """Result of notification send."""
    
    success: bool
    channel: NotificationChannel
    message_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Notification:
    """A notification message."""
    
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Optional[Dict[str, Any]] = None
    channels: Optional[List[NotificationChannel]] = None


class NotificationService:
    """
    Multi-channel notification service.
    
    Supports sending alerts via:
    - Telegram
    - Discord
    - Email
    - Custom webhooks
    
    Example:
        config = NotificationConfig.from_env()
        notifier = NotificationService(config)
        
        # Send notification
        await notifier.send_notification(
            Notification(
                title="Trade Executed",
                message="Bought 1 ETH at $2000",
                priority=NotificationPriority.HIGH
            )
        )
        
        # Send to specific channel
        await notifier.send_telegram("Price alert: ETH above $2500!")
    """
    
    def __init__(self, config: NotificationConfig):
        """
        Initialize notification service.
        
        Args:
            config: Notification configuration
        """
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def send_notification(
        self,
        notification: Notification
    ) -> List[NotificationResult]:
        """
        Send notification to all configured channels.
        
        Args:
            notification: Notification to send
        
        Returns:
            List of results for each channel
        """
        results = []
        
        # Determine channels
        channels = notification.channels or self.config.enabled_channels
        
        # Check priority threshold
        priority_order = [
            NotificationPriority.LOW,
            NotificationPriority.NORMAL,
            NotificationPriority.HIGH,
            NotificationPriority.CRITICAL
        ]
        
        if priority_order.index(notification.priority) < priority_order.index(self.config.min_priority):
            logger.debug(f"Notification below minimum priority: {notification.priority}")
            return results
        
        # Send to each channel
        tasks = []
        
        for channel in channels:
            if channel == NotificationChannel.TELEGRAM:
                tasks.append(self._send_telegram(notification))
            elif channel == NotificationChannel.DISCORD:
                tasks.append(self._send_discord(notification))
            elif channel == NotificationChannel.EMAIL:
                tasks.append(self._send_email(notification))
            elif channel == NotificationChannel.WEBHOOK:
                tasks.append(self._send_webhooks(notification))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(NotificationResult(
                        success=False,
                        channel=channels[i],
                        error=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            results = processed_results
        
        return results
    
    async def _send_telegram(self, notification: Notification) -> NotificationResult:
        """Send Telegram notification."""
        if not self.config.telegram_bot_token or not self.config.telegram_chat_id:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.TELEGRAM,
                error="Telegram not configured"
            )
        
        try:
            session = await self._get_session()
            
            # Format message
            text = f"*{notification.title}*\n\n{notification.message}"
            
            if notification.priority == NotificationPriority.CRITICAL:
                text = f"🚨 {text}"
            elif notification.priority == NotificationPriority.HIGH:
                text = f"⚠️ {text}"
            
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            
            async with session.post(url, json={
                "chat_id": self.config.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }) as response:
                data = await response.json()
                
                if data.get("ok"):
                    return NotificationResult(
                        success=True,
                        channel=NotificationChannel.TELEGRAM,
                        message_id=str(data["result"]["message_id"])
                    )
                else:
                    return NotificationResult(
                        success=False,
                        channel=NotificationChannel.TELEGRAM,
                        error=data.get("description", "Unknown error")
                    )
                    
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            return NotificationResult(
                success=False,
                channel=NotificationChannel.TELEGRAM,
                error=str(e)
            )
    
    async def _send_discord(self, notification: Notification) -> NotificationResult:
        """Send Discord webhook notification."""
        if not self.config.discord_webhook_url:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.DISCORD,
                error="Discord not configured"
            )
        
        try:
            session = await self._get_session()
            
            # Build embed
            color_map = {
                NotificationPriority.LOW: 0x808080,
                NotificationPriority.NORMAL: 0x0099ff,
                NotificationPriority.HIGH: 0xffcc00,
                NotificationPriority.CRITICAL: 0xff0000,
            }
            
            embed = {
                "title": notification.title,
                "description": notification.message,
                "color": color_map.get(notification.priority, 0x0099ff)
            }
            
            if notification.data:
                embed["fields"] = [
                    {"name": k, "value": str(v), "inline": True}
                    for k, v in notification.data.items()
                ]
            
            async with session.post(
                self.config.discord_webhook_url,
                json={"embeds": [embed]}
            ) as response:
                if response.status in (200, 204):
                    return NotificationResult(
                        success=True,
                        channel=NotificationChannel.DISCORD
                    )
                else:
                    text = await response.text()
                    return NotificationResult(
                        success=False,
                        channel=NotificationChannel.DISCORD,
                        error=f"HTTP {response.status}: {text}"
                    )
                    
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")
            return NotificationResult(
                success=False,
                channel=NotificationChannel.DISCORD,
                error=str(e)
            )
    
    async def _send_email(self, notification: Notification) -> NotificationResult:
        """Send email notification."""
        if not all([
            self.config.smtp_host,
            self.config.smtp_user,
            self.config.email_from,
            self.config.email_to
        ]):
            return NotificationResult(
                success=False,
                channel=NotificationChannel.EMAIL,
                error="Email not configured"
            )
        
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg["From"] = self.config.email_from
            msg["To"] = ", ".join(self.config.email_to)
            msg["Subject"] = f"[Crypto Sniper] {notification.title}"
            
            body = f"{notification.message}\n\n"
            if notification.data:
                body += "Details:\n"
                for k, v in notification.data.items():
                    body += f"  {k}: {v}\n"
            
            msg.attach(MIMEText(body, "plain"))
            
            await aiosmtplib.send(
                msg,
                hostname=self.config.smtp_host,
                port=self.config.smtp_port,
                username=self.config.smtp_user,
                password=self.config.smtp_password,
                start_tls=True
            )
            
            return NotificationResult(
                success=True,
                channel=NotificationChannel.EMAIL
            )
            
        except ImportError:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.EMAIL,
                error="aiosmtplib not installed"
            )
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return NotificationResult(
                success=False,
                channel=NotificationChannel.EMAIL,
                error=str(e)
            )
    
    async def _send_webhooks(self, notification: Notification) -> NotificationResult:
        """Send to custom webhooks."""
        if not self.config.webhook_urls:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.WEBHOOK,
                error="No webhooks configured"
            )
        
        try:
            session = await self._get_session()
            
            payload = {
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority.value,
                "data": notification.data or {}
            }
            
            results = []
            for url in self.config.webhook_urls:
                try:
                    async with session.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        results.append(response.status < 400)
                except Exception as e:
                    logger.warning(f"Webhook {url} failed: {e}")
                    results.append(False)
            
            success_count = sum(results)
            
            if success_count == len(self.config.webhook_urls):
                return NotificationResult(
                    success=True,
                    channel=NotificationChannel.WEBHOOK
                )
            else:
                return NotificationResult(
                    success=False,
                    channel=NotificationChannel.WEBHOOK,
                    error=f"{len(results) - success_count} webhooks failed"
                )
                
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return NotificationResult(
                success=False,
                channel=NotificationChannel.WEBHOOK,
                error=str(e)
            )
    
    # Convenience methods
    
    async def send_telegram(self, message: str, title: str = "Alert") -> NotificationResult:
        """Send Telegram message directly."""
        return await self._send_telegram(Notification(title=title, message=message))
    
    async def send_discord(self, message: str, title: str = "Alert") -> NotificationResult:
        """Send Discord message directly."""
        return await self._send_discord(Notification(title=title, message=message))
    
    async def alert_trade(
        self,
        action: str,
        token: str,
        amount: str,
        price: str,
        tx_hash: Optional[str] = None
    ) -> List[NotificationResult]:
        """Send trade alert."""
        return await self.send_notification(Notification(
            title=f"Trade Executed: {action} {token}",
            message=f"{action} {amount} {token} at ${price}",
            priority=NotificationPriority.HIGH,
            data={
                "action": action,
                "token": token,
                "amount": amount,
                "price": price,
                "tx_hash": tx_hash
            }
        ))
    
    async def alert_price(
        self,
        token: str,
        price: str,
        change_percent: str
    ) -> List[NotificationResult]:
        """Send price alert."""
        return await self.send_notification(Notification(
            title=f"Price Alert: {token}",
            message=f"{token} is now ${price} ({change_percent}%)",
            priority=NotificationPriority.NORMAL,
            data={
                "token": token,
                "price": price,
                "change": change_percent
            }
        ))
    
    async def alert_error(
        self,
        error_type: str,
        message: str
    ) -> List[NotificationResult]:
        """Send error alert."""
        return await self.send_notification(Notification(
            title=f"Error: {error_type}",
            message=message,
            priority=NotificationPriority.CRITICAL
        ))
