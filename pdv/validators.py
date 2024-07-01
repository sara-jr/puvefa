from django.core.validators import RegexValidator


def make_non_whitespace_validator(message=None, code=None):
   return RegexValidator(r'\S+', message, code, None, 0) 
