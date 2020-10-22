from django.contrib.auth.password_validation import MinimumLengthValidator, \
    CommonPasswordValidator, NumericPasswordValidator, UserAttributeSimilarityValidator
from django.utils.translation import ngettext
from difflib import SequenceMatcher
import re
from django.core.exceptions import (
    FieldDoesNotExist, ValidationError,
)
from django.utils.html import format_html
from django.utils.functional import lazy

# https://docs.djangoproject.com/en/2.0/_modules/django/contrib/auth/password_validation/#MinimumLengthValidator


class MyMinimumLengthValidator(MinimumLengthValidator):
    # update this definition with your custom messages
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Пароль занадто короткий. Пароль має містити хоча б %(min_length)d символів",
                    "Пароль занадто короткий. Пароль має містити хоча б %(min_length)d символів",
                    self.min_length
                ),
            code='password_too_short',
            params={'min_length': self.min_length}
            )

class MyCommonPasswordValidator(CommonPasswordValidator):
    """
    Validate whether the password is a common password.

    The password is rejected if it occurs in a provided list of passwords,
    which may be gzipped. The list Django ships with contains 20000 common
    passwords (lowercased and deduplicated), created by Royce Williams:
    https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
    The password list must be lowercased to match the comparison in validate().
    """

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                ("Цей пароль занадто простий"),
                code='password_too_common',
            )

class MyNumericPasswordValidator(NumericPasswordValidator):
    """
    Validate whether the password is alphanumeric.
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                ("Пароль не може складатися лише з цифр"),
                code='password_entirely_numeric',
            )

class MyUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        ("Пароль не має містити інформацію з вашого аккаунту"),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )

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