"""CP4 — Graceful shutdown."""

from __future__ import annotations

import signal


class Lifecycle:
    """Giữ trạng thái vòng đời của process."""

    def __init__(self) -> None:
        self.shutting_down = False

        # Handler cũ, ví dụ handler của uvicorn
        self._previous: dict = {}

    def request_shutdown(self, signum=None, frame=None) -> None:
        """Signal handler: đánh dấu process đang tắt dần."""

        # 1. Báo app đang trong quá trình shutdown
        self.shutting_down = True

        # 2. Gọi lại handler cũ nếu có
        previous = self._previous.get(signum)

        if callable(previous):
            previous(signum, frame)

    def install(self) -> None:
        """Đăng ký handler cho SIGTERM và SIGINT."""

        for sig in (signal.SIGTERM, signal.SIGINT):
            # Nhớ handler hiện tại trước khi ghi đè
            self._previous[sig] = signal.getsignal(sig)

            # Đăng ký handler của chúng ta
            signal.signal(sig, self.request_shutdown)


# Một instance dùng chung cho cả app
lifecycle = Lifecycle()