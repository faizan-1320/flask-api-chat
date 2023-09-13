import re

def emailRegex(email):
    EmailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(EmailRegex,email):
        response = {'Please enter valid email'}
        return response