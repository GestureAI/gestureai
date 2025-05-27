from fastapi.requests import Request

from core.jinja_context import templates


def show_test_page(req: Request):
    """
    Function to render a test page.
    This function is intended to be used with a web framework that supports rendering templates.
    """
    # Assuming we have a template rendering function available
    return templates.TemplateResponse(req, "test.jinja", {"key": "Some value"})
