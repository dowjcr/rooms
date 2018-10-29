"""
EMAIL
Defines some methods to send email notifications to users.
Author Cameron O'Connor.
"""


from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Student
FROM_EMAIL = "no-reply@downingjcr.co.uk"


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
        html_message = render_to_string('roomballot/emails/syndicate-failed.html', {'student': student})
        plain_message = """
        Hey! Unfortunately, someone rejected their invite to your syndicate, so it has been dissolved. To create
        a new syndicate, visit https://ballot.downingjcr.co.uk.
        """
        send_mail(subject, plain_message, FROM_EMAIL, recipient_list, html_message=html_message)


# ============= ROOM SELECTED =================
# Sends confirmation email to user that they have
# selected their room.

def selected_room(student, room):
    subject = student.first_name + ", you've selected your room."
    recipient_list = [student.user_id + "@cam.ac.uk"]
    html_message = render_to_string('roomballot/emails/room-selected.html', {'student': student,
                                                                             'room': room})
    plain_message = """
    Hey, thanks for selecting your room! You can view your selection on the Room Balloting System
    by visiting https://ballot.downingjcr.co.uk.
    """
    send_mail(subject, plain_message, FROM_EMAIL, recipient_list, html_message=html_message)


# ============= INVITE REVIEW =================
# Sends an email inviting the user to review their
# room.

def invite_review():
    for student in Student.objects.all():
        subject = student.first_name + ", review your room!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        html_message = render_to_string('roomballot/emails/review-room.html', {'student': student})
        plain_message = """
        Hey, Downing JCR here. Perhaps you'd like to review the room you're living in this year? Please
        visit https://ballot.downingjcr.co.uk.
        """
        send_mail(subject, plain_message, FROM_EMAIL, recipient_list, html_message=html_message)