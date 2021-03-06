# -*- coding: utf-8 -*-
#imports
from __future__ import division
from __future__ import absolute_import
from flask import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash, Markup, current_app
from datetime import datetime
import subprocess
import codecs, re

md_re = re.compile(ur"<[^>]*>|[　-㄀＀-￯\n¶]+|\t[^\n]+\n|\$[^;]+;")

dictab = {'hydcd1' : u'漢語大詞典',
          'hydcd' : u'漢語大詞典',
          'hydzd' : u'漢語大字典',
          'sanli' : u'三禮辭典',
          'daikanwa' : u'大漢和辞典',
          'koga' : u'禅語字典',
          'guoyu' : u'國語辭典',
          'abc' : u'ABC漢英詞典',
          'lyt' : u'林語堂當代漢英詞典',
          'cedict' : u'漢英詞典',
          'daojiao' : u'道教大辭典',
          'fks' : u'佛光佛學大辭典',
          'handedic' : u'漢德詞典',
          'dfb' : u'丁福報佛學大辭典',
          'unihan' : u'Unicode 字典',
          'kanwa' : u'發音',
          'kangxi' : u'康熙字典',
          'pinyin' : u'羅馬拼音',
          'loc' : u'其他詞典',
          'je' : u'日英仏教辞典',
          'kg' : u'葛藤語箋',
          'ina' : u'稲垣久雄:Zen Glossary',
          'iwa' : u'岩波仏教辞典',
          'zgd' : u'禪學大辭典',
          'oda' : u'織田佛教大辭典',
          'mz' : u'望月佛教大辭典',
          'matthews' : u'Matthews Chinese English Dictionary',
          'naka' : u'佛教語大辭典',
          'yo' : u'横井日英禪語辭典',
          'zgo' : u'禅の語録',
          'zhongwen' : u'中文大辭典',
          'bsk' : u'佛書解説大辭典',
          'bcs' : u'佛教漢梵大辭典',
          'zd' : u'Zen Dust',
          'ku' : u'ku',
          'sks' : u'sks',
          'guxun' : u'故訓匯纂',
          } 

try:
    import redis
except:
    pass

try:
    r = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
except:
    r = nil

app = Flask(__name__, static_folder='static')
app.config.from_object('local_settings')
idxdir = app.config['IDXDIR']
#dicurl = app.config['DICURL']
dicurl = "dic:"
#loginmanager=LoginManager()

    
@app.route('/search', methods=['GET', 'POST',])
def searchtext(count=20, start=None, n=20):
    key = request.values.get('query', '')
#    rep = "\n%s:" % (request.values.get('rep', 'ZB'))
    count=int(request.values.get('count', count))
    start=int(request.values.get('start', 0))
    #/Users/Shared/md/index"
    #subprocess.call(['bzgrep -H ^龍二  /Users/Shared/md/index/79/795e*.idx*'], stdout=of, shell=True )
    #ox = subprocess.check_output(['bzgrep -H ^%s  /Users/Shared/md/index/%s/%s*.idx*' % (key[1:], ("%4.4x" % (ord(key[0])))[0:2], "%4.4x" % (ord(key[0])))], shell=True )
    if len(key) > 0:
        try:
            ox = subprocess.check_output(['bzgrep -H ^%s  %s/%s/%s*.idx* | cut -d : -f 2-' % (key[1:],
              idxdir,  ("%4.4x" % (ord(key[0])))[0:2], "%4.4x" % (ord(key[0])))], shell=True )
#            ox = rep.join(ox.split('\n'))
        except subprocess.CalledProcessError:
            ox = "ERROR"
    else:
        return "400 please submit searchkey as parameter 'query'."
    return ox


@app.route('/getfile', methods=['GET',])
def getfile():
    #the filename is of the form ZB1a/ZB1a0001/ZB1a0001_002.txt 
    filename = request.values.get('filename', '')
    try:
        datei = "%s/%s" % (app.config['TXTDIR'], filename)
        print datei
        fn = codecs.open(datei)
    except:
        return "Not found"
    return Response ("\n%s" % (fn.read(-1)),  content_type="text/plain;charset=UTF-8")


# dic
def formatle(l, e):
    "formats the location entry"
    ec = e.split('-')
    if l == "daikanwa":
        return "[[%sdkw/p%s-%s][%s : %s]]" % (dicurl, ec[0][1:], ec[1][1:], dictab[l], e)
    elif l == "hydzd" :
        return "[[%shydzd/hydzd-%s][%s : %s]]" % (dicurl, ec[1], dictab[l], e)
    #comment the next two lines to link to the cached files on the server
    elif l == "kangxi":
        return "[[http://www.kangxizidian.com/kangxi/%4.4d.gif][%s : %s]]" % (int(e), dictab[l], e)
    elif l in ["koga", "ina", "bcs", "naka", "zgd", "sanli", "kangxi"] :
        if "," in e:
            v = e.split(',')[0]
        else:
            v = e
        v = re.sub('[a-z]', '', v)
        try:
            return "[[%s%s/%s-p%4.4d][%s : %s]]" % (dicurl, l, l, int(v), dictab[l], e)
        except:
            return "%s : %s" % (dictab[l], e)
            
    elif l == "yo":
        ec = e.split(',')
        return "[[%syokoi/yokoi-p%4.4d][%s : %s]]" % (dicurl, int(ec[0]), dictab[l], e)
    elif l == "mz":
        v = e.split(',')[0]
        v = v.split('p')
        return "[[%smz/vol%2.2d/mz-v%2.2d-p%4.4d][%s : %s]]" % (dicurl, int(v[0][1:]), int(v[0][1:]), int(re.sub('[a-z]', '', v[1])),  dictab[l], e)
    elif l == "je":
        ec = e.split('/')
        if ec[0] == '---':
            v = re.sub('[a-z]', '', ec[1])
        else:
            v = re.sub('[a-z]', '', ec[0])
        return "[[%sjeb/jeb-p%4.4d][%s : %s]]" % (dicurl, int(v), dictab[l], e)
    elif l == "zhongwen":
        # zhongwen : V09-p14425-1
        return "[[%szhwdcd/zhwdcd-p%5.5d][%s : %s]]" % (dicurl, int(ec[1][1:]), dictab[l], e)
    else:
        try:
            return "%s : %s" % (dictab[l], e)
        except:
            return "%s : %s" % (l, e)
            
def dicentry(key):
    if r:
        try:
            d = r.hgetall(key)
        except:
            return "no result"
        try:
            d.pop('dummy')
        except:
            pass
        if len(d) > 0:
            ks = d.keys()
            ks.sort()
            s = "** %s (%s)" % (key, len(d))
            xtr = ""
            ytr = ""
            df=[]
            lc=[]
            hy=[]
            seen=[]
            for a in ks:
                k = a.split('-')
                if k[0] == 'loc':
                    lc.append(formatle(k[1], d[a]))
                else:
                    if k[1] == 'kanwa':
                        xtr +=  " " + d[a]
                    if k[1] == 'abc':
                        ytr += " " + d[a]
                    if k[1] == 'hydcd1':
                        hy.append("**** %s: %s\n" % ("".join(k[2:]), d[a]))
                    elif k[1] in seen:
                        df.append("%s: %s\n" % ("".join(k[2:]), d[a]))
                    else:
                        if len(k) > 1:
                            df.append("*** %s\n%s: %s\n" % (dictab[k[1]], "".join(k[2:]), d[a]))
                        else:
                            df.append("*** %s\n%s\n" % (dictab[k[1]],  d[a]))
                        seen.append(k[1])
            if len(hy) > 0:
                hyr = "*** %s\n%s\n" % (dictab['hydcd1'],  "".join(hy))
            else:
                hyr = ""
            if len(df) > 0:
                dfr = "%s\n" % ("".join(df))
            else:
                dfr = ""
            if len(s) + len(xtr) + len(ytr) > 100:
                dx = 100 - len(s) - len(xtr) 
#                print dx
                ytr = ytr[0:dx]
            xtr = ytr = ""
            return "%s%s%s\n%s%s*** %s\n%s\n" % (s, xtr, ytr, hyr , dfr, dictab['loc'] , "\n".join(lc))
        else:
            return ""
    else:
        return "no redis"


@app.route('/procline', methods=['GET',])
def procline():
    l = request.values.get('query', '')
#    print l
    l = md_re.sub("", l)
#    print l
    de = []
    try:
        for i in range(0, len(l)):
            j = i+1
            res = dicentry(l[i:j])
            de.append(res)
            while res and j < len(l):
                j += 1
                res = dicentry(l[i:j])
                de.append(res)
        return "\n%s" % ("".join(de))
    except:
        return "Not Found: %s " % (l)

def prevnext(page):
    p = page.split('-')
    if p[-1].startswith ('p'):
        n= int(p[-1][1:])
        fn = fn = "%%%d.%dd" % (len(p[-1]) - 1, len(p[-1]) - 1)
        prev = "%s-p%s" % ("-".join(p[:-1]), fn % (n - 1) )
        next = "%s-p%s" % ("-".join(p[:-1]), fn % (n + 1) )
    else:
        n= int(p[-1])
        fn = fn = "%%%d.%dd" % (len(p[-1]), len(p[-1]))
        prev = "%s-%s" % ("-".join(p[:-1]), fn % (n - 1) )
        next = "%s-%s" % ("-".join(p[:-1]), fn % (n + 1) )
    return prev, next
        
@app.route('/dicpage/<dic>/<page>', methods=['GET',])
def dicpage(dic=None,page=None):
#    pn = "a", "b"
    pn = prevnext(page)
    us = url_for('static', filename='dic')
    return """<html>
<body>
<img src="%s/%s/%s.png" style="width:100%%;"/>
<a href="/dicpage/%s" type="button" id="btnPrev" >%s</a>
<a href="/dicpage/%s" type="button" id="btnNext">%s</a>
</body>
</html>""" % (us, dic, page, "%s/%s" % (dic, pn[0]), pn[0], "%s/%s" % (dic, pn[1]), pn[1])

@app.route('/dic', methods=['GET',])
def searchdic():
    key = request.values.get('query', '')
    return dicentry(key)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
