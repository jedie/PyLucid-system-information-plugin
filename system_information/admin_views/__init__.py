# coding: utf-8

from django.conf import settings

from pylucid_project.apps.pylucid.models import PageTree

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("system info")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="python info", title="Display some system information.",
        url_name="SysInfo-system_info"
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="process manager", title="Process Manager",
        url_name="SysInfo-process_manager"
    )

    return "\n".join(output)
