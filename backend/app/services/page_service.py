from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from core.jinja_context import templates
from services import telemetry_service
from utils.helpers import get_avg_min_max


def show_login_page(req: Request, is_valid: bool):
    if is_valid:
        return RedirectResponse("/api/admin/")

    return templates.TemplateResponse(req, "login.jinja")


def show_404_page():
    return RedirectResponse("/api/admin/")


def show_live_page(req: Request, is_valid: bool):
    if is_valid is False:
        return RedirectResponse("/api/admin/login")

    return templates.TemplateResponse(req, "live.jinja")


def show_panel_page(req: Request, is_valid: bool):
    if is_valid is False:
        return RedirectResponse("/api/admin/login")

    tel_for_last_5_min = telemetry_service.get_lasts_yonger(5)
    analyze_5_min = get_avg_min_max(tel_for_last_5_min)

    tel_for_last_30_min = telemetry_service.get_lasts_yonger(30)
    analyze_30_min = get_avg_min_max(tel_for_last_30_min)

    tel_for_last_4h = telemetry_service.get_lasts_yonger(60 * 4)
    analyze_4h = get_avg_min_max(tel_for_last_4h)

    tel_for_last_24h = telemetry_service.get_lasts_yonger(60 * 24)
    analyze_24h = get_avg_min_max(tel_for_last_24h)

    data = {
        "5m": analyze_5_min,
        "30m": analyze_30_min,
        "4h": analyze_4h,
        "24h": analyze_24h,
    }

    return templates.TemplateResponse(req, "panel.jinja", {"analyzes": data})


def show_lasts_responses_page(req: Request, is_valid: bool):
    if is_valid is False:
        return RedirectResponse("/api/admin/login")

    telemetries = telemetry_service.get_lasts_n(100)

    # round the precision to 4 decimal places
    for telemetry in telemetries:
        telemetry.precision = round(telemetry.precision, 4)

    data = {
        "telemetries": telemetries,
    }

    return templates.TemplateResponse(req, "lasts_responses.jinja", data)
