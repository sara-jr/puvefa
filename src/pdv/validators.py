from django.core.validators import RegexValidator


def make_non_whitespace_validator(message=None, code=None):
   return RegexValidator(r'\S+', message, code, None, 0) 


def make_name_validator(message=None, code=None):
   '''
   Crea un validador para nombres formados por al menos dos letras con o sin acento separados por espacio
   Utiliza la expresión regular:^[A-Za-zÀ-ÿ']{2,}[A-Za-zÀ-ÿ' ]*$
   '''
   return RegexValidator(r"^[A-Za-zÀ-ÿ']{2,}[A-Za-zÀ-ÿ' ]*$", message, code)
