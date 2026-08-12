class OpenRouterError(Exception):
    """Base error for OpenRouter integration."""


class OpenRouterConfigError(OpenRouterError):
    """Missing or invalid OpenRouter configuration."""


class OpenRouterResponseError(OpenRouterError):
    """Unexpected or malformed OpenRouter response."""
