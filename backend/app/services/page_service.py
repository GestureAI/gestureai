from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from core.jinja_context import templates


def show_login_page(req: Request, is_valid: bool):
    if is_valid:
        return RedirectResponse("/api/admin/")

    return templates.TemplateResponse(req, "login.jinja")


def show_404_page(req: Request):
    pass


def show_panel_page(req: Request, is_valid: bool):
    if is_valid is False:
        return RedirectResponse("/api/admin/login")

    return templates.TemplateResponse(req, "panel.jinja")
