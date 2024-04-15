# standard import
import logging

# from sib_api_v3_sdk.rest import ApiException
# import sib_api_v3_sdk

# core django imports
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from django.core import signing
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Third-party imports
from random import choice, SystemRandom
from string import digits, ascii_uppercase, ascii_lowercase
from rest_framework import status


validator_ascii = RegexValidator(
    regex=r"^[\x00-\x7F]*$", message="Only ASCII characters allowed"
)
validator_pan_no = RegexValidator(
    regex=r"^[A-Z]{5}\d{4}[A-Z]$", message="Please provide a valid pan number"
)

logger = logging.getLogger()


def upload_location(instance, filename):
    ext_set = filename.split(".")
    model = str(instance.__class__.__name__).lower()
    return "%s/%s.%s" % (model, timezone.now(), ext_set[-1])


def generate_random_string(length=5):
    digit_len = length // 2
    alpha_len = length - digit_len
    return "".join(
        [choice(digits) for _ in range(digit_len)]
        + [choice(ascii_lowercase) for _ in range(alpha_len)]
    )


def generate_response_dict(status="error", data={}, meta={}, message="no message"):
    return {"status": status, "message": message, "data": data, "meta": meta}


def get_mail_config():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDIN_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(
        name="Youyog", email=settings.EMAIL_SENDER
    )
    mail_dict = {"api_instance": api_instance, "senderSmtp": senderSmtp}
    return mail_dict


def sendewelcomemail(id, subject, to_email):
    message = f'<p>Thank you for subscribing Click the link here and set the password<a href="{settings.EMAIL_URL}{id}">Click Here!</a></p>'
    mail_config = get_mail_config()
    sendTo = sib_api_v3_sdk.SendSmtpEmailTo(email=to_email, name=to_email)
    arrTo = [sendTo]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=mail_config["senderSmtp"],
        to=arrTo,
        html_content=message,
        subject=subject,
    )
    try:
        api_response = mail_config["api_instance"].send_transac_email(send_smtp_email)
    except ApiException as e:
        logger.info("Error", e)
        return status.HTTP_400_BAD_REQUEST
    return status.HTTP_200_OK


def sendemail(id, to_email):
    subject = "Reset Your Password "
    message = f'<p>Click the link here and set the password<a href="{settings.EMAIL_URL}{id}">Click Here!</a></p>'
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDIN_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(
        name="test", email=settings.EMAIL_SENDER
    )
    sendTo = sib_api_v3_sdk.SendSmtpEmailTo(email=to_email, name=to_email)
    arrTo = [sendTo]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=senderSmtp, to=arrTo, html_content=message, subject=subject
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        logger.info("Error", e)
        return status.HTTP_400_BAD_REQUEST
    return status.HTTP_200_OK


def string_encrypt(string):
    value = signing.dumps(string)
    return value


def decrypt_string(string):
    value = signing.loads(string)
    return value


def generate_response_dict(status="error", data={}, meta={}, message="no message"):
    return {"status": status, "message": message, "data": data, "meta": meta}


def get_set_password_subject_message(id, frontend_redirect_url):
    subject = "Reset Your Password"
    # Construct the message with a link to set the password
    message = f'<p>Click the link here and set the password<a href="{frontend_redirect_url}{id}"/"">Click Here!</a></p>'
    return {"subject": subject, "message": message}


def get_subscription_request_subject_message(id, frontend_redirect_url):
    subject = "Subscription Request Approval"
    # Construct the message with a link to set the password
    message = f'<p>Thank you for subscribing Click the link here and set the password<a href="{frontend_redirect_url}{id}"/">Click Here!</a></p>'
    return {"subject": subject, "message": message}


def paginate(request, qs, nb):
    paginator = Paginator(qs, nb)  # Show nb objects per page
    page = request.GET.get("page")
    # page = 2
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)

    # Get the index of the current page
    index = objects.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]
    last_page_number = int(math.ceil(len(qs) / nb))

    return [objects, page_range, last_page_number]


def create_slug(instance, new_slug=None, append_string=None):
    if new_slug is not None:
        slug = new_slug
    elif instance.slug:
        slug = instance.slug
    elif hasattr(instance, "title"):
        slug = slugify(instance.title)
    elif hasattr(instance, "name"):
        slug = slugify(instance.name)
    elif hasattr(instance, "tag"):
        slug = slugify(instance.tag)
    else:
        slug = None
    if append_string and slug:
        slug = slugify(append_string + slug)
    if slug:
        qs = instance.__class__.objects.filter(slug=slug).order_by("-id")
        exists = True if qs.exists() and qs.first().id != instance.id else False
        if exists:
            # print qs
            # print "old_slug",slug
            new_slug = "%s-%s" % (slug, generate_random_string(length=5))
            # print "new_slug",new_slug
            return create_slug(instance, new_slug=new_slug)
        if len(slug) > 50:
            slug = slug[:44] + "-" + generate_random_string(length=5)
        if not slug:
            slug = generate_random_string(length=5)
        return slug
    else:
        return None
