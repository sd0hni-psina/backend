from .models import Notification

# def create_notification(recipient, sender, type, content_object=None):
#     if recipient == sender:
#         return
    
#     notification = Notification.objects.filter(
#         recipient=recipient,
#         sender=sender,
#         type=type,
#         content_object=content_object,
#     )
#     return notification

def create_notification(recipient, sender, type, content_object=None):
    """Создать уведомление если не существует"""
    if recipient == sender:
        return None
    
    # Используем get_or_create для избежания дубликатов
    from django.contrib.contenttypes.models import ContentType
    
    kwargs = {
        'recipient': recipient,
        'sender': sender,
        'type': type,
    }
    
    if content_object:
        kwargs['content_type'] = ContentType.objects.get_for_model(content_object)
        kwargs['object_id'] = content_object.id
    
    notification, created = Notification.objects.get_or_create(**kwargs)
    return notification