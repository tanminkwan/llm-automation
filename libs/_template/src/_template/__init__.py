"""표준 검증용 reference 모듈.

이 모듈은 Phase 0 의 ``_template`` 으로, 워크스페이스 표준
(uv workspace · ruff · mypy · pytest · multi-stage Dockerfile)
이 정상 동작함을 증명하기 위한 카나리아입니다.

운영 코드 아닙니다. 후속 phase 에서 import 대상이 아닙니다.
"""

from _template.greeter import Clock, Greeter
from _template.settings import TemplateSettings

__all__ = ["Clock", "Greeter", "TemplateSettings"]
__version__ = "0.0.1"
