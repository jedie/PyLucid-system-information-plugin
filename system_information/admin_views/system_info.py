# coding: utf-8

import sys
import os
import resource
import pwd

from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to



class StructTable(object):
    def __init__(self, struct_data):
        assert isinstance(struct_data, (tuple, list))
        self.struct_data = struct_data

    def as_table(self):
        output = "<table>\n<tr>\n"
        attrs = []
        for attr, desc in self.ATTR_INFO:
            output += "\t<th>%s</th>\n" % desc
            attrs.append(attr)
        output += "</tr>\n"

        for obj in self.struct_data:
            output += "<tr>\n"
            for attr in attrs:
                output += "\t<td>%s</td>\n" % getattr(obj, attr)
            output += "</tr>\n"

        output += "</table>\n"
        return mark_safe(output)


class PwdTable(StructTable):
    # from http://docs.python.org/library/pwd.html
    ATTR_INFO = (
        ("pw_name", "Login name"),
        ("pw_passwd", "Optional encrypted password"),
        ("pw_uid", "Numerical user ID"),
        ("pw_gid", "Numerical group ID"),
        ("pw_gecos", "User name or comment field"),
        ("pw_dir", "User home directory"),
        ("pw_shell", "User command interpreter"),
    )

class RusageTable(StructTable):
    # from http://docs.python.org/library/resource.html#resource.getrusage
    ATTR_INFO = (
        ('ru_utime', 'time in user mode (float)'),
        ('ru_stime', 'time in system mode (float)'),
        ('ru_maxrss', 'maximum resident set size'),
        ('ru_ixrss', 'shared memory size'),
        ('ru_idrss', 'unshared memory size'),
        ('ru_isrss', 'unshared stack size'),
        ('ru_minflt', 'page faults not requiring I/O'),
        ('ru_majflt', 'page faults requiring I/O'),
        ('ru_nswap', 'number of swap outs'),
        ('ru_inblock', 'block input operations'),
        ('ru_oublock', 'block output operations'),
        ('ru_msgsnd', 'messages sent'),
        ('ru_msgrcv', 'messages received'),
        ('ru_nsignals', 'signals received'),
        ('ru_nvcsw', 'voluntary context switches'),
        ('ru_nivcsw', 'involuntary context switches')
    )


def safe_get(mod, attr_name):
    try:
        attr = getattr(mod, attr_name)
        if callable(attr):
            return attr(), True
        else:
            return attr, False
    except Exception, err:
        return ("[Error: %s]" % err, None)


def info(mod, attr_name, info):
    value, is_callable = safe_get(mod, attr_name)

    code = "%s.%s" % (mod.__name__, attr_name)
    if is_callable:
        code += "()"

    return (code, value, info)


@check_permissions(superuser_only=True)
@render_to("system_information/system_info.html")
def system_info(request):
    context = {
        "title": "System info",
    }
    try:
        context["loadavg"] = os.getloadavg()
    except OSError, err:
        context["loadavg_err"] = "[Error: %s]" % err


    context["sys"] = [
        info(sys, "version",
            "version number of the Python interpreter plus additional information"
        ),
        info(sys, "subversion",
            "Subversion information of the Python interpreter"
        ),
        info(sys, "argv",
            "command line arguments passed to a Python script"
        ),
        info(sys, "exec_prefix",
            "site-specific directory prefix where the platform-dependent Python files are installed"
        ),
        info(sys, "prefix",
            "site-specific directory prefix where the platform independent Python files are installed"
        ),
        info(sys, "executable",
            "name of the executable binary for the Python interpreter"
        ),
        info(sys, "flags",
            "status of command line flags"
        ),
        info(sys, "getdefaultencoding",
            "current default string encoding used by the Unicode implementation"
        ),
        info(sys, "getfilesystemencoding",
            "encoding used to convert Unicode filenames into system file names"
        ),
    ]

    context["os"] = [
        info(os, "ctermid",
            "filename corresponding to the controlling terminal of the process"
        ),
        info(os, "times",
            "accumulated (processor or other) times, in seconds"
        ),
        info(os, "getegid",
            "effective group id of the current process"
        ),
        info(os, "geteuid",
            "current process’s effective user id"
        ),
        info(os, "getgid",
            "real group id of the current process"
        ),
        info(os, "uname",
            "sysname, nodename, release, version, machine"
        ),
        info(os, "getlogin",
            "name of the user logged in on the controlling terminal of the process"
        ),
    ]
    context["resource"] = [
        info(resource, "getpagesize", "number of bytes in a system page")
    ]
    context["rusage_self"] = RusageTable([resource.getrusage(resource.RUSAGE_SELF)]).as_table()
    context["rusage_child"] = RusageTable([resource.getrusage(resource.RUSAGE_CHILDREN)]).as_table()

    context["pwall"] = PwdTable(pwd.getpwall()).as_table()

    return context
