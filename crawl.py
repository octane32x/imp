# WEB CRAWL

from random import choice
from os import mkdir, listdir
from os.path import isdir
from socket import gethostbyname
from urllib.request import urlopen

URL_PRE = 'https://'
TODO = 'ip/todo.txt'
DEAD = 'ip/dead.txt'
ALPH = 'alph.txt'
FREQ = 'freq.txt'

def pull(url):
  try:
    fp = urlopen(URL_PRE + url, timeout=1.0)
    html = fp.read().decode("utf8")
    fp.close()
    return html
  except:
    pass
  return ''

def lit(c):
  return True if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or \
                 (c >= '0' and c <= '9') or c == '_' else False

def clean(link):
  i = 0
  while i < len(link):
    if link[i] == '\\':
      link = link[:i] + link[i+1:]
      continue
    i += 1
  if link[-1] == '/': link = link[:-1]
  i = 0
  if link[:5] == 'https': i = 5
  elif link[:4] == 'http': i = 4
  if i >= len(link): return ''
  if link[i] == ':': i += 1
  if i >= len(link): return ''
  if link[i] == '/': i += 1
  if i >= len(link): return ''
  if link[i] == '/': i += 1
  if i >= len(link): return ''
  if link[i:i+4] == 'www.': i += 4
  if i >= len(link): return ''
  return link[i:]

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
      if key in r.keys():
        r[key] += val
      else:
        r[key] = val
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
    if tok in toks.keys():
      toks[tok] += 1
    else:
      toks[tok] = 1
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
    if link != '': r[link] = True
    i = j+1
  return r

# Data
urls = {} # {url : True}
todo = {} # {ip : {url : from_url}}
dead = {} # {ip : {url : from_url}}
pop = {}  # {ip : {'todo' : {url : from_url}, \
          #        'dead' : {url : from_url}, \
          #        'pop'  : {url : from_url}, \
          #        'tokens' : {token : count}}}
toks = {} # {token : count}

def write_web():
  f = open(ALPH, 'w')
  a = sorted(toks.keys())
  for key in a:
    f.write(key + ' : ' + str(toks[key]) + '\n')
  f.close()

  f = open(FREQ, 'w')
  b = dict(sorted(toks.items(), key=lambda item: item[1], reverse=True))
  for key in b.keys():
    f.write(key + ' : ' + str(b[key]) + '\n')
  f.close()

  f = open(TODO, 'w')
  for ip in todo.keys():
    f.write(ip + '\n')
    for url in todo[ip].keys():
      f.write(url + ' ' + todo[ip][url] + '\n')
    f.write('\n')
  f.close()

  f = open(DEAD, 'w')
  for ip in dead.keys():
    f.write(ip + '\n')
    for url in dead[ip].keys():
      f.write(url + ' ' + dead[ip][url] + '\n')
    f.write('\n')
  f.close()

def write_ip(ip):
  if ip not in listdir('./ip/'):
    mkdir('./ip/' + ip)

  f = open('./ip/' + ip + '/todo.txt', 'w')
  for url in pop[ip]['todo'].keys():
    f.write(url + ' ' + pop[ip]['todo'][url] + '\n')
  f.close()

  f = open('./ip/' + ip + '/dead.txt', 'w')
  for url in pop[ip]['dead'].keys():
    f.write(url + ' ' + pop[ip]['dead'][url] + '\n')
  f.close()

  f = open('./ip/' + ip + '/pop.txt', 'w')
  for url in pop[ip]['pop'].keys():
    f.write(url + ' ' + pop[ip]['pop'][url] + '\n')
  f.close()

  f = open('./ip/' + ip + '/tokens.txt', 'w')
  for tok in pop[ip]['tokens'].keys():
    f.write(tok + ' ' + str(pop[ip]['tokens'][tok]) + '\n')
  f.close()

# MAIN

# Unvisited IPs
f = open(TODO, 'r')
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
    urls[tok[0]] = True
    m[tok[0]] = tok[1]
    i += 1
  todo[ip] = m
  i += 1

# Dead IPs
f = open(DEAD, 'r')
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
    urls[tok[0]] = True
    m[tok[0]] = tok[1]
    i += 1
  dead[ip] = m
  i += 1

# Populated IPs
dirs = listdir('./ip/')
for d in dirs:
  if not isdir('./ip/' + d): continue
  f = open('./ip/' + d + '/todo.txt', 'r')
  s = f.read()
  f.close()
  lines = s.split('\n')[:-1]
  m = {}
  for line in lines:
    tok = line.split(' ')
    urls[tok[0]] = True
    m[tok[0]] = tok[1]
  pop[d] = {}
  pop[d]['todo'] = m

  f = open('./ip/' + d + '/dead.txt', 'r')
  s = f.read()
  f.close()
  lines = s.split('\n')[:-1]
  m = {}
  for line in lines:
    tok = line.split(' ')
    urls[tok[0]] = True
    m[tok[0]] = tok[1]
  pop[d]['dead'] = m

  f = open('./ip/' + d + '/pop.txt', 'r')
  s = f.read()
  f.close()
  lines = s.split('\n')[:-1]
  m = {}
  for line in lines:
    tok = line.split(' ')
    urls[tok[0]] = True
    m[tok[0]] = tok[1]
  pop[d]['pop'] = m

  f = open('./ip/' + d + '/tokens.txt', 'r')
  s = f.read()
  f.close()
  lines = s.split('\n')[:-1]
  m = {}
  for line in lines:
    tok = line.split(' ')
    m[tok[0]] = int(tok[1])
  pop[d]['tokens'] = m

# All tokens
for ip in pop.keys():
  for tok in pop[ip]['tokens'].keys():
    count = pop[ip]['tokens'][tok]
    if tok in toks.keys():
      toks[tok] += count
    else:
      toks[tok] = count

# Main loop
while True:
  while len(todo) > 0:
    print()
    print(str(len(todo)) + ' pending IPs')
    print(str(len(pop)) + ' IPs with data')
    print(str(len(toks)) + ' tokens')
    print()

    ip, m = choice(list(todo.items()))
    del todo[ip]
    _dead = {}
    while len(m) > 0:
      url, urlf = choice(list(m.items()))
      del m[url]

      print(ip + '  ' + url)
      html = pull(url) #time
      if html == '':
        _dead[url] = urlf
        continue

      # Create new IP profile
      m2 = {}
      m2['todo'] = m
      m2['dead'] = _dead
      m2['pop'] = {url : urlf}
      t = tokens(html)
      toks = merge([toks, t])
      m2['tokens'] = t
      pop[ip] = m2
      write_ip(ip)

      a = links(html)
      for link in a:
        if link in urls.keys(): continue
        urls[link] = True
        try:
          ipn = gethostbyname(cut(link))
          if ipn in todo.keys():
            todo[ipn][link] = url
          elif ipn in dead.keys():
            todo[ipn] = dead[ipn]
            todo[ipn][link] = url
            del dead[ipn]
          elif ipn in pop.keys():
            pop[ipn]['todo'][link] = url
            write_ip(ipn)
          else:
            todo[ipn] = {link : url}
        except: continue
      break

    if len(m) == 0 and len(_dead) > 0 and ip not in pop.keys():
      print('DEAD')
      dead[ip] = _dead
    write_web()
