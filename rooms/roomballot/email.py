"""
EMAIL
Defines some methods to send email notifications to users.
Author Cameron O'Connor.
"""


from django.core.mail import send_mail
from .models import Student
FROM_EMAIL = "no-reply@jcr.dow.cam.ac.uk"


# ============ INVITE SELECTION ==================
# Invites the given student to log in and select their
# room.

def invite_selection(student):
    subject = student.first_name + ", time to pick your room!"
    recipient_list = [student.user_id + "@cam.ac.uk"]
    message = "Time to select your room!"
    send_mail(subject, message, FROM_EMAIL, recipient_list)


# ============ INVITE SYNDICATE ==================
# Sends invitations to the other members of the given
# syndicate, inviting them to accept.

def invite_syndicate(syndicate):
    owner_id = syndicate.owner_id
    students = Student.objects.filter(syndicate=syndicate).exclude(user_id=owner_id)
    for student in students:
        subject = student.first_name + ", you've been invited to a syndicate!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        message = "You've been invited!"
        send_mail(subject, message, FROM_EMAIL, recipient_list)


# ============ COMPLETED SYNDICATE ================
# Sends emails confirming that the syndicate is now
# complete, since everyone has accepted.

def completed_syndicate(syndicate):
    students = Student.objects.filter(syndicate=syndicate)
    for student in students:
        subject = student.first_name + ", your syndicate is complete!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        message = "Syndicate is complete."
        send_mail(subject, message, FROM_EMAIL, recipient_list)


# ============ FAILED SYNDICATE ================
# Sends emails confirming that the syndicate has
# failed, since somebody rejected the invitation.

def failed_syndicate(syndicate):
    students = Student.objects.filter(syndicate=syndicate)
    for student in students:
        subject = student.first_name + ", your syndicate has failed."
        recipient_list = [student.user_id + "@cam.ac.uk"]
        message = "Syndicate failed."
        send_mail(subject, message, FROM_EMAIL, recipient_list)


# ============= ROOM SELECTED =================
# Sends confirmation email to user that they have
# selected their room.

def selected_room(student):
    subject = student.first_name + ", you've selected your room."
    recipient_list = [student.user_id + "@cam.ac.uk"]
    message = "Room has been selected. Details below:"
    send_mail(subject, message, FROM_EMAIL, recipient_list)