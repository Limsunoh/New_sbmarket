from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r"^[\w.@+-]+\Z"
    message = _("유효한 사용자 아이디를 입력합니다. 이 값에는 문자, " "숫자 및 @/./+/-/_ 문자만 포함할 수 있습니다.")
    flags = 0
