import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def release_expired_seat_locks():
    try:
        redis_client = settings.REDIS_CLIENT
        pattern = "lock:session:*:seat:*"
        
        expired_count = 0
        keys = list(redis_client.scan_iter(match=pattern))
        
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl == -1:
                redis_client.delete(key)
                expired_count += 1
                logger.info(f"Released expired lock: {key}")
        
        logger.info(f"Released {expired_count} expired seat locks")
        return expired_count
        
    except Exception as e:
        logger.error(f"Error releasing expired locks: {e}")
        raise


@shared_task
def send_ticket_confirmation(ticket_id, user_email):
    try:
        subject = "CineReserve - Confirmação de Ingresso"
        message = f"""
            Olá,

            Seu ingresso foi confirmado com sucesso!

            ID do ingresso: {ticket_id}

            Apresente este código na entrada do cinema.

            Obrigado por escolher o CineReserve!
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent to {user_email} for ticket {ticket_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
        raise
