"""
EMAIL
Defines some methods to send email notifications to users.
Author Cameron O'Connor.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Student, Review, Room
import logging

FROM_EMAIL = "Downing JCR <no-reply@downingjcr.co.uk>"
LOG_FILE = 'roomballot.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# ============ INVITE SELECTION ==================
# Invites the given student to log in and select their
# room.

def invite_selection(student):
    subject = student.first_name + ", time to pick your room!"
    recipient_list = [student.user_id + "@cam.ac.uk"]
    html_message = render_to_string('roomballot/emails/selection-invite.html', {'student': student})
    message = "Time to select your room! Go to https://ballot.downingjcr.co.uk now."
    send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
    logger.info("Invited selection [" + student.user_id + "]")


# ============ INVITE SYNDICATE ==================
# Sends invitations to the other members of the given
# syndicate, inviting them to accept.

def invite_syndicate(syndicate):
    owner_id = syndicate.owner_id
    students = Student.objects.filter(syndicate=syndicate).exclude(user_id=owner_id)
    for student in students:
        subject = student.first_name + ", you've been invited to a syndicate!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        html_message = render_to_string('roomballot/emails/syndicate-invite.html', {'student': student})
        message = "You've been invited to a syndicate! Go to https://ballot.downingjcr.co.uk to respond to the invite."
        send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
        logger.info("Invited to syndicate [" + student.user_id + "]")


# ============ COMPLETED SYNDICATE ================
# Sends emails confirming that the syndicate is now
# complete, since everyone has accepted.

def completed_syndicate(syndicate):
    students = Student.objects.filter(syndicate=syndicate)
    for student in students:
        subject = student.first_name + ", your syndicate is complete!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        html_message = render_to_string('roomballot/emails/syndicate-complete.html', {'student': student})
        message = "Hey! Your syndicate is complete, great job! You can view it at https://ballot.downingjcr.co.uk."
        send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
        logger.info("Notified syndicate complete [" + student.user_id + "]")


# ============ FAILED SYNDICATE ================
# Sends emails confirming that the syndicate has
# failed, since somebody rejected the invitation.

def failed_syndicate(syndicate):
    students = Student.objects.filter(syndicate=syndicate)
    for student in students:
        subject = student.first_name + ", your syndicate has been dissolved."
        recipient_list = [student.user_id + "@cam.ac.uk"]
        html_message = render_to_string('roomballot/emails/syndicate-failed.html', {'student': student})
        plain_message = """
        Hey! Unfortunately, someone rejected their invite to your syndicate, so it has been dissolved. To create
        a new syndicate, visit https://ballot.downingjcr.co.uk.
        """
        send_mail(subject, plain_message, FROM_EMAIL, recipient_list, html_message=html_message)
        logger.info("Notified syndicate failed [" + student.user_id + "]")


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
    logger.info("Notified room allocated [" + student.user_id + "]")


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
        logger.info("Initial review invite [" + student.user_id + "]")


# ============= REMIND REVIEW =================
# Sends an email inviting the user to review their
# room.

def remind_review():
    for room in Room.objects.exclude(taken_by=None):
        student = room.taken_by
        reviews_left = Review.objects.filter(author_id=student.user_id, room=room)
        if reviews_left.count() == 0:
            subject = student.first_name + ", review your room!"
            recipient_list = [student.user_id + "@cam.ac.uk"]
            html_message = render_to_string('roomballot/emails/review-room-reminder.html', {'student': student})
            plain_message = """
                Hey, Downing JCR here. Looks like you haven't reviewed your room yet! Please
                visit https://ballot.downingjcr.co.uk.
                """
            send_mail(subject, plain_message, FROM_EMAIL, recipient_list, html_message=html_message)
            logger.info("Reminded to leave review [" + student.user_id + "]")


# ============= CONFIRM REVIEW ================
# Sends an email thanking the user for leaving
# a review.

def confirm_review(student):
    subject = student.first_name + ", thanks for reviewing your room!"
    recipient_list = [student.user_id + "@cam.ac.uk"]
    html_message = render_to_string('roomballot/emails/review-confirmation.html', {'student': student})
    message = "Thanks for reviewing your room! We appreciate you :)"
    send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
    logger.info("Acknowledged review left [" + student.user_id + "]")


# ============= INVITE BALLOT =================
# Sends an email explaining the ballot to first-years,
# and inviting them to create their syndicates.

def invite_ballot():
    for student in Student.objects.filter(year=1):
        subject = "Important room ballot information!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        html_message = render_to_string('roomballot/emails/invite-ballot.html', {'student': student})
        message = "Please view this email as HTML"
        send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
        logger.info('Sent invitation message [' + student.user_id + ']')


# apology

def invite_ballot_error():
    for student in Student.objects.filter(syndicate=None):
        subject = "Sorry!"
        recipient_list = [student.user_id + "@cam.ac.uk"]
        html_message = render_to_string('roomballot/emails/invite-ballot-error.html', {'student': student})
        message = "Please view this email as HTML"
        send_mail(subject, message, FROM_EMAIL, recipient_list, html_message=html_message)
        logger.info('Sent error sorry message [' + student.user_id + ']')