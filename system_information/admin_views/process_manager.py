# coding: utf-8

"""
    see also:
        http://www.kernel.org/doc/man-pages/online/pages/man5/proc.5.html
"""

import os
import pwd
import subprocess

from django.utils.safestring import mark_safe

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from system_information.forms import KillForm
from django.http import HttpResponseRedirect



class ProcessInfo(object):
    def __init__(self, pid):
        self.pid = pid

        self.status_dict = {}
        self.raw_status = self.collect_proc_status(pid)
        self.uid = int(self.status_dict["Uid"][0])

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
            self.status_dict[key] = value

        return raw_status

    def get_html_cmdline(self):
        try:
            cmdline_path = "/proc/%i/cmdline" % self.pid
            cmdline = open(cmdline_path, "r").read()
            cmdline = cmdline.strip().split("\0")
            cmdline[0] = "<strong>%s</strong>" % cmdline[0]
            cmdline = mark_safe(" ".join(cmdline))
        except Exception, err:
            return "[Error: %s]" % err
        return cmdline




class ProcInfo(object):
    def __init__(self, uid):
        self.uid = uid

        self.total_thread_count = 0
        self.total_process_count = 0
        self.uid_thread_count = 0
        self.uid_process_count = 0
        self.proc_info = {}

        self.collect_proc_info()

    def collect_proc_info(self):
        for filename in os.listdir("/proc"):
            path = os.path.join("/proc", filename)
            if not os.path.isdir(path):
                continue
            try:
                pid = int(filename)
            except ValueError:
                continue

            self.total_process_count += 1
            process_info = ProcessInfo(pid)

            thread_count = int(process_info.status_dict["Threads"])
            self.total_thread_count += thread_count

            if self.uid and self.uid != process_info.uid:
                continue

            self.uid_process_count += 1
            self.uid_thread_count += thread_count

            self.proc_info[pid] = process_info


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
            process_info = ProcessInfo(pid)
            if process_info.uid != uid:
                request.page_msg.error("Process %i is not a user own process!" % pid)
            else:
                sig = int(form.cleaned_data["sig"])
                request.page_msg("Send signal %s to %s" % (sig, pid))
                os.kill(pid, sig)

            return HttpResponseRedirect(request.path)
        else:
            request.page_msg(form.errors)


    cmd = ["/usr/bin/top", "-bn1", "-u%s" % os.getlogin()]
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        top_output = process.stdout.read()
        top_output += process.stderr.read()
    except Exception, err:
        top_output = "[Error: %s]" % err

    proc_info = ProcInfo(uid=uid)

    for pid, process_info in proc_info.proc_info.iteritems():
        process_info.form = KillForm(initial={"pid":pid})

    context = {
        "title": "Process Manager",

        "form_url": request.path,

        "top_cmd": " ".join(cmd),
        "top_output": top_output,

        "proc_info": proc_info,
    }

    return context
