

import sys,os



if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ServerAudits.settings")

    import django
    django.setup() #手动注册django所有的APP
    from audit.backend import user_interactive   #要在app手动注册后执行
    obj = user_interactive.UserShell()
    obj.start()