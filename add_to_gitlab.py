#!/usr/bin/python
# -*- coding: utf-8 -*-


import os, re, git, sys, subprocess, codecs


import gitlab
from sh import git
from time import sleep
start="/tmp/text"
gl = gitlab.Gitlab('http://zb.kanripo.org', 'hzj3TXjgzysKdqcVPmSF')
# Connect to get the current user
gl.auth()

def proc_dir(arg, dirname, names):
    n = "$".join(names)
    if ".git$" in n:
        fn = dirname.split('/')[-1]
        print dirname
        h = codecs.open("%s/%s.org" % (dirname, fn), 'r', 'utf-8')
        tit = h.readline()
        h.close()
        tit = re.sub(ur'#\+TITLE: ', '', tit)
        #get the group
        print fn, tit
        gptmp = re.split('([0-9])', fn, 1)
        gp = "".join(gptmp[0:2]) + gptmp[2][0]
        #get the group id
        gpid = 0
        for g in gl.Group():
            if g.name.lower() == gp.lower():
                gpid = g.id
        if gpid == 0:
            g = gl.Group({'name' : gp, 'path' : gp.lower()})
            g.save()
            gpid = g.id
        p = gl.Project({'name' : fn.lower(), 'description' : tit, 'wiki_enabled': False})
        p.save()
        sleep(0.5)
        pid = p.id
        print pid, gpid
        g = gl.Group(gpid)
        try:
            g.transfer_project(pid)
        except:
            print "What the heck!"
        p = gl.Project(pid)
        rep = git.bake(_cwd="%s" % (dirname))
        try:
            rep.remote("add", "origin", p.ssh_url_to_repo)
        except:
            pass
        for b in rep.branch(_iter=True):
            b=re.sub(ur'\\x1b[^m]*m', '', b)
            if b.startswith('*'):
                print b
                rep.push("-u", "origin",  b.split(' ')[1][:-1])
        for b in rep.branch(_iter=True):
            b=re.sub(ur'\\x1b[^m]*m', '', b)
            if not(b.startswith('*')):
                print b
                rep.push("-u", "origin",  b.strip())
        


os.path.walk(start, proc_dir, '')
