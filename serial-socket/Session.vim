let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Docker/instrument-services/serial-socket
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +60 instruments/instrument.py
badd +0 instruments/bronkhorst/bronkhorst.py
badd +0 socket_service/client.py
argglobal
silent! argdel *
$argadd instruments/instrument.py
$argadd instruments/bronkhorst/bronkhorst.py
edit instruments/instrument.py
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winminheight=1 winminwidth=1 winheight=1 winwidth=1
exe '1resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 1resize ' . ((&columns * 102 + 102) / 205)
exe '2resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 2resize ' . ((&columns * 102 + 102) / 205)
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
28
normal! zo
243
normal! zo
252
normal! zo
258
normal! zo
259
normal! zo
260
normal! zo
262
normal! zo
264
normal! zo
265
normal! zo
267
normal! zo
272
normal! zo
273
normal! zo
274
normal! zo
276
normal! zo
278
normal! zo
279
normal! zo
280
normal! zo
280
normal! zo
280
normal! zo
280
normal! zo
282
normal! zo
285
normal! zo
286
normal! zo
243
normal! zc
291
normal! zo
299
normal! zo
305
normal! zo
306
normal! zo
307
normal! zo
309
normal! zo
311
normal! zo
312
normal! zo
314
normal! zo
319
normal! zo
320
normal! zo
321
normal! zo
323
normal! zo
325
normal! zo
326
normal! zo
327
normal! zo
327
normal! zo
327
normal! zo
327
normal! zo
329
normal! zo
332
normal! zo
333
normal! zo
338
normal! zo
let s:l = 305 - ((6 * winheight(0) + 12) / 25)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
305
normal! 0
wincmd w
argglobal
if bufexists('instruments/instrument.py') | buffer instruments/instrument.py | else | edit instruments/instrument.py | endif
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
28
normal! zo
243
normal! zo
252
normal! zo
258
normal! zo
259
normal! zo
260
normal! zo
262
normal! zo
264
normal! zo
265
normal! zo
267
normal! zo
272
normal! zo
273
normal! zo
274
normal! zo
276
normal! zo
278
normal! zo
279
normal! zo
280
normal! zo
280
normal! zo
280
normal! zo
280
normal! zo
282
normal! zo
285
normal! zo
286
normal! zo
243
normal! zc
291
normal! zo
299
normal! zo
305
normal! zo
306
normal! zo
307
normal! zo
309
normal! zo
311
normal! zo
312
normal! zo
314
normal! zo
319
normal! zo
320
normal! zo
321
normal! zo
323
normal! zo
325
normal! zo
326
normal! zo
327
normal! zo
327
normal! zo
327
normal! zo
327
normal! zo
329
normal! zo
332
normal! zo
333
normal! zo
338
normal! zo
367
normal! zo
375
normal! zo
380
normal! zo
384
normal! zo
388
normal! zo
390
normal! zo
392
normal! zo
394
normal! zo
395
normal! zo
let s:l = 306 - ((12 * winheight(0) + 12) / 25)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
306
normal! 017|
wincmd w
argglobal
if bufexists('socket_service/client.py') | buffer socket_service/client.py | else | edit socket_service/client.py | endif
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=3
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 32 - ((31 * winheight(0) + 25) / 51)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
32
normal! 05|
wincmd w
2wincmd w
exe '1resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 1resize ' . ((&columns * 102 + 102) / 205)
exe '2resize ' . ((&lines * 25 + 26) / 53)
exe 'vert 2resize ' . ((&columns * 102 + 102) / 205)
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
