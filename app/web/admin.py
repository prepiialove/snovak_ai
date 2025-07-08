from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.services import crud
from app.web.schemas import ServiceData, RawText
from app.services.ai import get_service_data_from_text
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session: AsyncSession = Depends(get_async_session)):
    services = await crud.get_all_services(session)
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "services": services})


@router.get("/add", response_class=HTMLResponse)
async def add_service_form(request: Request):
    return templates.TemplateResponse("admin/add_service.html", {"request": request})


@router.post("/process-text", response_class=JSONResponse)
async def process_text_for_admin(raw_text: RawText):
    service_data = await asyncio.to_thread(get_service_data_from_text, raw_text.text)
    if not service_data:
        return JSONResponse(content={"error": "Failed to process text"}, status_code=500)
    return service_data.model_dump()


@router.post("/add")
async def add_service(
    session: AsyncSession = Depends(get_async_session),
    name: str = Form(...),
    category: str = Form(...),
    address: str = Form(None),
    phone: str = Form(None),
    schedule: str = Form(None),
    social_media: str = Form(None),
    description: str = Form(None),
):
    service_data = ServiceData(
        name=name,
        category=category,
        address=address,
        phone=phone,
        schedule=schedule,
        social_media=social_media,
        description=description,
    )
    await crud.create_service(session, service_data.model_dump())
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/edit/{service_id}", response_class=HTMLResponse)
async def edit_service_form(request: Request, service_id: int, session: AsyncSession = Depends(get_async_session)):
    service = await crud.get_service_by_id(session, service_id)
    return templates.TemplateResponse("admin/edit_service.html", {"request": request, "service": service})


@router.post("/edit/{service_id}")
async def edit_service(
    service_id: int,
    session: AsyncSession = Depends(get_async_session),
    name: str = Form(...),
    category: str = Form(...),
    address: str = Form(None),
    phone: str = Form(None),
    schedule: str = Form(None),
    social_media: str = Form(None),
    description: str = Form(None),
):
    service_data = ServiceData(
        name=name,
        category=category,
        address=address,
        phone=phone,
        schedule=schedule,
        social_media=social_media,
        description=description,
    )
    await crud.update_service(session, service_id, service_data)
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/delete/{service_id}")
async def delete_service(service_id: int, session: AsyncSession = Depends(get_async_session)):
    await crud.delete_service(session, service_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/categories", response_class=HTMLResponse)
async def list_categories(request: Request, session: AsyncSession = Depends(get_async_session)):
    categories = await crud.get_all_categories(session)
    return templates.TemplateResponse("admin/categories.html", {"request": request, "categories": categories})

@router.get("/categories/add", response_class=HTMLResponse)
async def add_category_form(request: Request):
    return templates.TemplateResponse("admin/add_category.html", {"request": request})

@router.post("/categories/add")
async def add_category(
    session: AsyncSession = Depends(get_async_session),
    name: str = Form(...),
    icon: str = Form(None),
):
    await crud.create_category(session, {"name": name, "icon": icon})
    return RedirectResponse(url="/admin/categories", status_code=303)

@router.get("/categories/edit/{category_id}", response_class=HTMLResponse)
async def edit_category_form(request: Request, category_id: int, session: AsyncSession = Depends(get_async_session)):
    category = await crud.get_category_by_id(session, category_id)
    return templates.TemplateResponse("admin/edit_category.html", {"request": request, "category": category})

@router.post("/categories/edit/{category_id}")
async def edit_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
    name: str = Form(...),
    icon: str = Form(None),
):
    await crud.update_category(session, category_id, {"name": name, "icon": icon})
    return RedirectResponse(url="/admin/categories", status_code=303)

@router.get("/categories/delete/{category_id}")
async def delete_category(category_id: int, session: AsyncSession = Depends(get_async_session)):
    await crud.delete_category(session, category_id)
    return RedirectResponse(url="/admin/categories", status_code=303)

@router.get("/menu", response_class=HTMLResponse)
async def list_menu_buttons(request: Request, session: AsyncSession = Depends(get_async_session)):
    buttons = await crud.get_all_menu_buttons(session)
    return templates.TemplateResponse("admin/menu.html", {"request": request, "buttons": buttons})

@router.get("/menu/add", response_class=HTMLResponse)
async def add_menu_button_form(request: Request, session: AsyncSession = Depends(get_async_session)):
    buttons = await crud.get_all_menu_buttons(session)
    return templates.TemplateResponse("admin/add_menu_button.html", {"request": request, "buttons": buttons})

@router.post("/menu/add")
async def add_menu_button(
    session: AsyncSession = Depends(get_async_session),
    text: str = Form(...),
    parent_id: int = Form(None),
):
    await crud.create_menu_button(session, {"text": text, "parent_id": parent_id})
    return RedirectResponse(url="/admin/menu", status_code=303)

@router.get("/menu/edit/{button_id}", response_class=HTMLResponse)
async def edit_menu_button_form(request: Request, button_id: int, session: AsyncSession = Depends(get_async_session)):
    button = await crud.get_menu_button_by_id(session, button_id)
    buttons = await crud.get_all_menu_buttons(session)
    return templates.TemplateResponse("admin/edit_menu_button.html", {"request": request, "button": button, "buttons": buttons})

@router.post("/menu/edit/{button_id}")
async def edit_menu_button(
    button_id: int,
    session: AsyncSession = Depends(get_async_session),
    text: str = Form(...),
    parent_id: int = Form(None),
):
    await crud.update_menu_button(session, button_id, {"text": text, "parent_id": parent_id})
    return RedirectResponse(url="/admin/menu", status_code=303)

@router.get("/menu/delete/{button_id}")
async def delete_menu_button(button_id: int, session: AsyncSession = Depends(get_async_session)):
    await crud.delete_menu_button(session, button_id)
    return RedirectResponse(url="/admin/menu", status_code=303)