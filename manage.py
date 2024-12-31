#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import ray

if os.name == 'posix':
    import grp
    # 仅在 Unix 系统上执行的代码
else:
    # 在 Windows 上执行的替代代码
    pass

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHON PATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # init ray
    ray.init()
    # Django
    main()
