from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.db import models
import datetime
from .models import VisitorSlot

class VisitorSlotMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Kosongkan slot yang tidak aktif lebih dari 5 minit
        timeout = timezone.now() - datetime.timedelta(minutes=5)
        VisitorSlot.objects.filter(last_active__lt=timeout).update(session_key=None)

        # Ambil slot yang tersedia untuk sesi semasa
        try:
            slot = VisitorSlot.objects.get(session_key=session_key)
        except VisitorSlot.DoesNotExist:
            slot = VisitorSlot.objects.filter(session_key__isnull=True).order_by('slot_number').first()
            if not slot:
                max_slot = VisitorSlot.objects.aggregate(models.Max('slot_number'))['slot_number__max'] or 0
                slot = VisitorSlot.objects.create(slot_number=max_slot + 1)
            slot.session_key = session_key

        slot.last_active = timezone.now()
        slot.save()
        request.visitor_slot = slot
