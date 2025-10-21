from .models import Notification

def create_notification(recipient, sender, type, content_object=None):
    if recipient == sender:
        return
    
    notification = Notification.objects.filter(
        recipient=recipient,
        sender=sender,
        type=type,
        content_object=content_object,
    )
    return notification