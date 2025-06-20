from typing import Any
from tools.google_calendar import GoogleCalendarTool
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class GoogleProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in GoogleCalendarTool.from_credentials(credentials).invoke(
                tool_parameters={"action": "fetch", "query": "Check my events"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
