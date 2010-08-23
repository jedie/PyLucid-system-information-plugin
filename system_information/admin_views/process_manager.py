# coding: utf-8

"""
    see also:
        http://www.kernel.org/doc/man-pages/online/pages/man5/proc.5.html
"""

import os
import pwd
import getpass
import subprocess

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from system_information.forms import KillForm




class ProcessInfo(dict):
    def __init__(self, pid):
        self.pid = pid

        raw_status = self.collect_proc_status(pid)
        dict.__setitem__(self, "raw_status", raw_status)

        self.uid = int(self["Uid"][0])

    def collect_proc_status(self, pid):
        status_path = "/proc/%i/status" % pid

        raw_status = open(status_path, "r").read()
        for line in raw_status.splitlines():
            try:
                key, value = line.split(":", 1)
            except Exception, err:
                print "Error: %s" % err
                print "raw line: %r" % line
                continue

            value = value.strip()
            if "\t" in value:
                value = value.split("\t")
            dict.__setitem__(self, key, value)

        return raw_status

    def get_html_cmdline(self):
        try:
            cwd_link = "/proc/%i/cwd" % self.pid
            cwd = os.path.realpath(cwd_link)
            cwd = cwd.rstrip("/")
        except Exception, err:
            cwd = "[Error: %s]" % err

        try:
            cmdline_path = "/proc/%i/cmdline" % self.pid
            cmdline = open(cmdline_path, "r").read()
            cmdline = cmdline.strip().split("\0")

            prog = cmdline[0].lstrip("/")
            args = " ".join(cmdline[1:])

            cmdline = mark_safe(
                "%s/<strong>%s</strong> %s" % (cwd, prog, args)
            )
        except Exception, err:
            return "[Error: %s]" % err

        return cmdline





class ProcInfo(list):
    def __init__(self, uid, request):
        self.uid = uid
        self.request = request

        self.total_thread_count = 0
        self.total_process_count = 0
        self.uid_thread_count = 0
        self.uid_process_count = 0

        self.collect_proc_info()

    def collect_proc_info(self):
        for filename in os.listdir("/proc"):
            if not filename.isdigit():
                continue

            path = os.path.join("/proc", filename)
            if not os.path.isdir(path):
                continue

            pid = int(filename)

            self.total_process_count += 1
            try:
                process_info = ProcessInfo(pid)
            except Exception, err:
                messages.error(self.request, "Ignore pid %s: %s" % (pid, err))
                continue

            thread_count = int(process_info["Threads"])
            self.total_thread_count += thread_count

            if self.uid and self.uid != process_info.uid:
                continue

            self.uid_process_count += 1
            self.uid_thread_count += thread_count

            list.append(self, process_info)


            #~ print "-"*79
            #~ for filename in os.listdir(path):
                #~ print "***", filename
                #~ if filename in ("pagemap", "smaps", "environ", "auxv", "numa_maps", "exe"):
                    #~ print "skip"
                    #~ continue
                #~ filepath = os.path.join(path, filename)
                #~ if os.path.isfile(filepath):
                    #~ try:
                        #~ print open(filepath, "r").read()#line()
                    #~ except Exception, err:
                        #~ print "[Err: %s]" % err
                #~ else:
                    #~ print "<dir>"


@check_permissions(superuser_only=True)
@render_to("system_information/process_manager.html")
def process_manager(request):

    uid = os.geteuid()

    if request.method == 'POST':
        form = KillForm(request.POST)
        if form.is_valid():
            pid = int(form.cleaned_data["pid"])
            try:
                process_info = ProcessInfo(pid)
            except IOError, err:
                messages.error(request, "Can't read process information for pid: %i: %s" % (pid, err))
            else:
                if process_info.uid != uid:
                    messages.error(request, "Process %i is not a user own process!" % pid)
                else:
                    sig = int(form.cleaned_data["sig"])
                    messages.info(request, "Send signal %s to %s" % (sig, pid))
                    os.kill(pid, sig)

            return HttpResponseRedirect(request.path)
        else:
            messages.info(request, repr(form.errors))

    try:
        # use getpass.getuser() instead of os.getlogin()
        # becuase getlogin doesn't work in any cases
        # see: http://www.python-forum.de/viewtopic.php?f=1&t=22878
        username = getpass.getuser()

        cmd = ["/usr/bin/top", "-bn1", "-U%s" % username]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        top_output = process.stdout.read()
        top_output += process.stderr.read()
    except Exception, err:
        cmd = ""
        top_output = "[Error: %s]" % err

    proc_info = ProcInfo(uid, request)

    for process_info in proc_info:
        process_info.form = KillForm(initial={"pid":process_info.pid})

    context = {
        "title": "Process Manager",

        "form_url": request.path,

        "top_cmd": " ".join(cmd),
        "top_output": top_output,

        "proc_info": proc_info,
        "pid": os.getpid(),
    }

    return context
