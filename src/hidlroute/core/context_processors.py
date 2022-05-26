from django.contrib import admin


def admin_menu(request):
    return admin.site.each_context(request)
