from django.utils.html import format_html
from django.utils.functional import lazy

def _custom_password_validators_help_text_html():
    """
    Return an HTML string with all help texts of all configured validators
    in an <ul>.
    """
    help_texts = ['Ваш пароль не має бути занадто схожим на вашу іншу особисту інформацію',
                              'Ваш пароль повинен містити щонайменше 8 символів',
                              'У паролі не повинні використовуватися тільки прості слова або загальновживані рими чи фрази',
                              'Ваш пароль не повинен містити тільки цифри']
    help_items = [format_html('<li>{}</li>', help_text) for help_text in help_texts]
    #<------------- append your hint here in help_items  ------------->
    return '<div class="helptext"><ul>%s</ul></div>' % ''.join(help_items) if help_items else ''


custom_password_validators_help_text_html =lazy(_custom_password_validators_help_text_html, str)