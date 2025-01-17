from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class HashtagValidator(RegexValidator):
    regex = r"^[^\s#@!$%^&*()]+$"
    message = _("해시태그는 띄어쓰기와 특수문자를 포함할 수 없습니다.")
    flags = 0
