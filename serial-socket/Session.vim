let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Docker/instrument-services/serial-socket
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +1 instruments/bronkhorst/bronkhorst.py
badd +1 instruments/instrument.py
badd +1 socket_service/socket_server.py
badd +1 socket_service/libserver.py
badd +1 instruments/bronkhorst/Dockerfile
argglobal
silent! argdel *
$argadd instruments/bronkhorst/bronkhorst.py
edit instruments/instrument.py
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
wincmd _ | wincmd |
split
1wincmd k
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winminheight=1 winminwidth=1 winheight=1 winwidth=1
exe 'vert 1resize ' . ((&columns * 102 + 102) / 205)
exe '2resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 2resize ' . ((&columns * 102 + 102) / 205)
exe '3resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 3resize ' . ((&columns * 102 + 102) / 205)
argglobal
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
23
normal! zo
60
normal! zo
192
normal! zo
201
normal! zo
202
normal! zo
206
normal! zo
207
normal! zo
209
normal! zo
210
normal! zo
214
normal! zo
215
normal! zo
192
normal! zc
294
normal! zo
296
normal! zo
297
normal! zo
304
normal! zo
305
normal! zo
309
normal! zo
316
normal! zo
321
normal! zo
322
normal! zo
324
normal! zo
327
normal! zo
333
normal! zo
336
normal! zo
342
normal! zo
346
normal! zo
348
normal! zo
350
normal! zo
352
normal! zo
294
normal! zc
357
normal! zo
360
normal! zo
363
normal! zo
373
normal! zo
377
normal! zo
let s:l = 377 - ((305 * winheight(0) + 25) / 51)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
377
normal! 019|
wincmd w
argglobal
if bufexists('socket_service/socket_server.py') | buffer socket_service/socket_server.py | else | edit socket_service/socket_server.py | endif
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
19
normal! zo
20
normal! zo
38
normal! zo
42
normal! zo
53
normal! zo
let s:l = 40 - ((25 * winheight(0) + 12) / 25)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
40
normal! 09|
wincmd w
argglobal
if bufexists('instruments/bronkhorst/bronkhorst.py') | buffer instruments/bronkhorst/bronkhorst.py | else | edit instruments/bronkhorst/bronkhorst.py | endif
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 4 - ((0 * winheight(0) + 12) / 25)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
4
normal! 0
wincmd w
exe 'vert 1resize ' . ((&columns * 102 + 102) / 205)
exe '2resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 2resize ' . ((&columns * 102 + 102) / 205)
exe '3resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 3resize ' . ((&columns * 102 + 102) / 205)
tabnext 1
if exists('s:wipebuf') && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 winminheight=1 winminwidth=1 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
