# your_app/signals.py
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def logout_previous_sessions(sender, request, user, **kwargs):
    # Get all sessions for the user
    current_session_key = request.session.session_key
    sessions = Session.objects.filter(session_key__isnull=False)

    for session in sessions:
        # Load session data
        data = session.get_decoded()
        # If session belongs to the logged-in user and is not the current session, delete it
        if data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
            session.delete()
