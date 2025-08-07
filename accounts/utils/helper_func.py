from django.utils.text import slugify
import os


def mask_email(email):
    """
    Function to mask an email address with asterisks and return the masked email.
    """
    try:
        username, domain = email.split('@')
        if len(username) > 2:
            masked_email = f"{username[0]}{'*' * (len(username) - 2)}{username[-1]}@{domain}"
        else:
            masked_email = f"{username}@{domain}"
        return masked_email
    except ValueError:
        return email


def account_image_upload_path(instance, filename):
    """
    Generate a custom upload path for the user's profile image.
    The filename includes a slugified version of the username.
    """
    # Slugify the username
    username_slug = slugify(instance.user.username)
    # Extract the file extension
    extension = filename.split('.')[-1]
    # Return the custom upload path
    return os.path.join('account', f"{username_slug}.{extension}")
