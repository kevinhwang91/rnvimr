let s:bufnr = -1
let s:winid = -1

function rnvimr#context#bufnr(...) abort
    let old = s:bufnr
    if a:0 == 1
        let s:bufnr = a:1
    endif
    return old
endfunction

function rnvimr#context#winid(...) abort
    let old = s:winid
    if a:0 == 1
        let s:winid = a:1
    endif
    return old
endfunction

function! rnvimr#context#check_point() abort
    let s:buf_cp_dict = {}
    for buf in filter(getbufinfo({'buflisted': 1}),
                \'v:val.changed == 0 && !empty(glob(v:val.name))')
        let s:buf_cp_dict[buf.bufnr] = buf.name
    endfor
endfunction

function! rnvimr#context#buf_wipe() abort
    let bw_list = []
    for bufnr_str in keys(filter(s:buf_cp_dict, 'empty(glob(v:val))'))
        let bufnr = str2nr(bufnr_str)
        if bufexists(bufnr) && empty(glob(fnamemodify(bufname(bufnr), ':p')))
            call add(bw_list, bufnr)
        endif
    endfor
    if len(bw_list) > 0
        " execute bwipeout last buffer before leaving floating window, it may cause this issue:
        " E5601: Cannot close window, only floating window would remain
        " use timer to delay bwipeout after leaving floating window
        call timer_start(0, {-> execute('silent! bwipeout ' . join(bw_list, ' '))})
    endif
endfunction
