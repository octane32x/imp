# WEB CRAWL
# Creates 'ip' directory

#! Good way to terminate without being mid-write?

from random import choice
from os import mkdir, listdir, stat
from os.path import isdir, isfile
from socket import gethostbyname
from urllib.request import urlopen

IP_DIR = './ip/'
FSUF = '.txt'
VIS = 'vis'
TODO = 'todo'
DEAD = 'dead'
POP = 'pop'
TOK = 'tokens'
IP_FILES = [TODO, DEAD, POP]

URL_PRE = 'https://'
TRASH = ['.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4']
START = ['rodonews.ru'] #'en.wikipedia.org/wiki/List_of_Wikipedias'

def pull(url):
  try:
    fp = urlopen(URL_PRE + url, timeout=1.0)
    html = fp.read().decode("utf8")
    fp.close()
    return html
  except: pass
  return ''

def lit(c):
  return True if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or \
                 (c >= '0' and c <= '9') or c == '_' else False

def starts(s, t):
  if len(t) > len(s): return False
  i = 0
  for i in range(len(t)):
    if s[i] != t[i]: return False
  return True

def contains(s, t):
  if len(t) > len(s): return False
  i = 0
  for i in range(len(s) - len(t) + 1):
    j = i
    f = True
    for k in range(len(t)):
      if s[j] != t[k]:
        f = False
        break
      j += 1
    if f: return True
  return False

def clean(link):
  i = 0
  while i < len(link):
    if link[i] == '\\':
      link = link[:i] + link[i+1:]
      continue
    i += 1
  if link[-1] == '/': link = link[:-1]
  strip = ['https://', 'http://', 'https:', 'http:', 'https', 'http', 'www.']
  for st in strip:
    if starts(link, st): link = link[len(st):]
  return link

def cut(link):
  i = 0
  while i < len(link) and link[i] != '/':
    i += 1
  if i == len(link): return link
  return link[:i]

def merge(maps):
  r = {}
  for m in maps:
    for key in m.keys():
      val = m[key]
      if key in r.keys(): r[key] += val
      else: r[key] = val
  return r

def tokens(html):
  toks = {}
  i = 0
  while i < len(html):
    if not lit(html[i]):
      i += 1
      continue
    tok = ''
    while i < len(html) and lit(html[i]):
      tok += html[i].lower()
      i += 1
    if tok in toks.keys(): toks[tok] += 1
    else: toks[tok] = 1
  return toks

def links(html):
  r = {}
  i = 0
  while i < len(html)-5:
    if html[i:i+5] != '"http':
      i += 1
      continue
    j = i+1
    while html[j] != '"':
      j += 1
    link = clean(html[i+1:j])
    f = False
    for junk in TRASH:
      if contains(link, junk):
        f = True
        break
    if (not f) and link != '': r[link] = True
    i = j+1
  return r

# Data
vis  = {} # {'urlhash:ip' : True}
pop  = {} # {ip : True}
todo = {} # {ip : {url : from_ip}}
dead = {} # {ip : {url : from_ip}}

# {'todo' : {url : from_ip},
#  'dead' : {url : from_ip},
#  'pop'  : {url : from_ip},
#  'tokens' : {tok : count}}
def load_ip(ip):
  m = {}
  if not isdir(IP_DIR + d): return m

  for fs in IP_FILES:
    f = open(IP_DIR + d + '/' + fs + FSUF, 'r')
    s = f.read()
    f.close()
    lines = s.split('\n')[:-1]
    mm = {}
    for line in lines:
      tok = line.split(' ')
      if len(tok) >= 2:
        mm[tok[0]] = tok[1]
    m[fs] = mm

  f = open(IP_DIR + d + '/' + TOK + FSUF, 'r')
  s = f.read()
  f.close()
  lines = s.split('\n')[:-1]
  mm = {}
  for line in lines:
    tok = line.split(' ')
    mm[tok[0]] = int(tok[1])
  m[TOK] = mm
  return m

def write_web():
  f = open(IP_DIR + VIS + FSUF, 'w')
  for n in vis.keys():
    f.write(n + '\n')
  f.close()

  f = open(IP_DIR + TODO + FSUF, 'w')
  for ip in todo.keys():
    f.write(ip + '\n')
    for url in todo[ip].keys():
      f.write(url + ' ' + todo[ip][url] + '\n')
    f.write('\n')
  f.close()

  f = open(IP_DIR + DEAD + FSUF, 'w')
  for ip in dead.keys():
    f.write(ip + '\n')
    for url in dead[ip].keys():
      f.write(url + ' ' + dead[ip][url] + '\n')
    f.write('\n')
  f.close()

def write_ip(ip, m):
  if ip not in listdir(IP_DIR):
    mkdir(IP_DIR + ip)

  for fs in IP_FILES:
    f = open(IP_DIR + ip + '/' + fs + FSUF, 'w')
    for url in m[fs].keys():
      f.write(url + ' ' + m[fs][url] + '\n')
    f.close()

  f = open(IP_DIR + ip + '/' + TOK + FSUF, 'w')
  for tok in m[TOK].keys():
    f.write(tok + ' ' + str(m[TOK][tok]) + '\n')
  f.close()

# MAIN

# Init env
if not isdir(IP_DIR):
  mkdir(IP_DIR)
ft = IP_DIR + VIS + FSUF
if not isfile(ft):
  f = open(ft, 'w')
  f.close()
ft = IP_DIR + TODO + FSUF
if not isfile(ft):
  f = open(ft, 'w')
  for url in START:
    ip = gethostbyname(cut(url))
    hs = str(hash(url)) + ':' + ip
    vis[hs] = True
    f.write(ip + '\n' + url + ' NULL\n\n')
  f.close()
ft = IP_DIR + DEAD + FSUF
if not isfile(ft):
  f = open(ft, 'w')
  f.close()

# Visited links
f = open(IP_DIR + VIS + FSUF, 'r')
s = f.read()
f.close()
lines = s.split('\n')[:-1]
i = 0
while i < len(lines):
  vis[lines[i]] = True
  i += 1

# IPs with data
dirs = listdir(IP_DIR)
for d in dirs:
  if isdir(IP_DIR + d):
    pop[d] = True

# Unvisited IPs
f = open(IP_DIR + TODO + FSUF, 'r')
s = f.read()
f.close()
lines = s.split('\n')[:-1]
i = 0
while i < len(lines):
  ip = lines[i]
  i += 1
  m = {}
  while i < len(lines) and lines[i] != '':
    tok = lines[i].split(' ')
    if len(tok) >= 2:
      m[tok[0]] = tok[1]
    i += 1
  todo[ip] = m
  i += 1

# Dead IPs
f = open(IP_DIR + DEAD + FSUF, 'r')
s = f.read()
f.close()
lines = s.split('\n')[:-1]
i = 0
while i < len(lines):
  ip = lines[i]
  i += 1
  m = {}
  while i < len(lines) and lines[i] != '':
    tok = lines[i].split(' ')
    if len(tok) >= 2:
      m[tok[0]] = tok[1]
    i += 1
  dead[ip] = m
  i += 1

# Main loop
while True:
  while len(todo) > 0:
    print()
    print('    ' + str(len(todo)) + ' pending IPs')
    print('    ' + str(len(pop)) + ' IPs with data')
    print('    ' + str(len(dead)) + ' dead IPs')

    b = 0
    #print()
    n = stat(IP_DIR + VIS + FSUF).st_size
    #print('vis ' + str(n))
    b += n
    n = stat(IP_DIR + TODO + FSUF).st_size
    #print('todo ' + str(n))
    b += n
    n = stat(IP_DIR + DEAD + FSUF).st_size
    #print('dead ' + str(n))
    b += n
    dirs = listdir(IP_DIR)
    for d in dirs:
      if not isdir(IP_DIR + d): continue
      n = 0
      n += stat(IP_DIR + d + '/' + TODO + FSUF).st_size
      n += stat(IP_DIR + d + '/' + DEAD + FSUF).st_size
      n += stat(IP_DIR + d + '/' + POP + FSUF).st_size
      n += stat(IP_DIR + d + '/' + TOK + FSUF).st_size
      b += n
    print('    ' + str(float(b) / (1024 * 1024)) + ' MB of data')
    print()

    ip, m = choice(list(todo.items()))
    del todo[ip]
    _dead = {}
    while len(m) > 0:
      if len(_dead) > 20: break
      url, urlf = choice(list(m.items()))
      del m[url]

      print(ip + '  ' + url)
      html = pull(url) #time
      if html == '':
        _dead[url] = urlf
        continue

      # Create new IP profile
      m2 = {}
      m2[TODO] = m
      m2[DEAD] = _dead
      m2[POP] = {url : urlf}
      t = tokens(html)
      print('-> ' + str(len(t)) + ' tokens')
      m2[TOK] = t
      write_ip(ip, m2)
      pop[ip] = True

      a = links(html)
      for link in a:
        try:
          ipn = gethostbyname(cut(link))
          if ipn == '0.0.0.0': exit(0) #!
          hs = str(hash(link)) + ':' + ipn
          if hs in vis.keys(): continue
          vis[hs] = True
          if ipn in todo.keys():
            todo[ipn][link] = url
          elif ipn in dead.keys():
            todo[ipn] = dead[ipn]
            todo[ipn][link] = url
            del dead[ipn]
          elif ipn in pop.keys():
            mm = load_ip(ipn)
            mm[TODO][link] = url
            write_ip(ipn, mm)
          else:
            todo[ipn] = {link : url}
        except: continue
      break

    if len(_dead) > 0 and ip not in pop.keys():
      print('DEAD')
      dead[ip] = _dead
    write_web()
