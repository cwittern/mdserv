# -*- coding: utf-8 -*-
#imports
from __future__ import division
from __future__ import absolute_import
from flask import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash, Markup, current_app
from datetime import datetime
import subprocess
import codecs, re

md_re = re.compile(ur"<[^>]*>|[　-㄀＀-￯\n¶]+|\t[^\n]+\n")

dictab = {'hydcd1' : u'漢語大詞典',
          'hydcd' : u'漢語大詞典',
          'hydzd' : u'漢語大字典',
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
#          '' : u'',
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
        fn = codecs.open("%s/%s" % (app.config['TXTDIR'], filename))
    except:
        return "Not found"
    return Response ("%s" % (fn.read(-1)),  content_type="text/plain;charset=UTF-8")


# dic
def formatle(l, e):
    "formats the location entry"
    ec = e.split('-')
    if l == "daikanwa":
        return "[[%sdkw/p%s-%s.djvu][%s : %s]]" % (dicurl, ec[0][1:], ec[1][1:], dictab[l], e)
    elif l == "hydzd" :
        return "[[%shydzd/hydzd-%s.djvu][%s : %s]]" % (dicurl, ec[1], dictab[l], e)
    elif l in ["koga", "ina", "bcs", "naka", "zgd"] :
        if "," in e:
            v = e.split(',')[0]
        else:
            v = e
        v = re.sub('[a-z]', '', v)
        return "[[%s%s/%s-p%4.4d.djvu][%s : %s]]" % (dicurl, l, l, int(v), dictab[l], e)
    elif l == "yo":
        ec = e.split(',')
        return "[[%syokoi/yokoi-p%4.4d.djvu][%s : %s]]" % (dicurl, int(ec[0]), dictab[l], e)
    elif l == "mz":
        v = e.split(',')[0]
        v = v.split('p')
        return "[[%smz/vol%2.2d/mz-v%2.2d-p%4.4d.djvu][%s : %s]]" % (dicurl, int(v[0][1:]), int(v[0][1:]), int(re.sub('[a-z]', '', v[1])),  dictab[l], e)
    elif l == "je":
        ec = e.split('/')
        v = re.sub('[a-z]', '', ec[0])
        return "[[%sjeb/jeb-p%4.4d.djvu][%s : %s]]" % (dicurl, int(v), dictab[l], e)
    elif l == "zhongwen":
        # zhongwen : V09-p14425-1
        return "[[%szhwdcd/%5.5d.djvu][%s : %s]]" % (dicurl, int(ec[1][1:]), dictab[l], e)
    else:
        try:
            return "%s : %s" % (dictab[l], e)
        except:
            return "%s : %s" % (l, e)
            
def dicentry(key):
    if r:
        d = r.hgetall(key)
        try:
            d.pop('dummy')
        except:
            pass
        if len(d) > 0:
            ks = d.keys()
            ks.sort()
            s = "** %s (%s)\n" % (key, len(d))
            df=[]
            lc=[]
            hy=[]
            seen=[]
            for a in ks:
                k = a.split('-')
                if k[0] == 'loc':
                    lc.append(formatle(k[1], d[a]))
                else:
#                    print k
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
            return "%s%s%s*** %s\n%s\n" % (s, hyr , dfr, dictab['loc'] , "\n".join(lc))
        else:
            return ""
    else:
        return "no redis"


@app.route('/procline', methods=['GET',])
def procline():
    l = request.values.get('query', '')
    l = md_re.sub("", l)
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


@app.route('/dic', methods=['GET',])
def searchdic():
    key = request.values.get('query', '')
    return dicentry(key)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
