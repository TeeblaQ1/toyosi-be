from django.core.mail import EmailMessage

class AuthUtil:
    def get_username(email):
        return email.split("@")[0]

class MailUtil:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data.get("email_subject"), body=data.get("email_body"), to=[data.get("to_email")])
        email.send()