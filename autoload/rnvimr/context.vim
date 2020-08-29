let s:buf_handle = -1
let s:win_handle = -1

function rnvimr#context#get_buf_handle() abort
    return s:buf_handle
endfunction

function rnvimr#context#set_buf_handle(handle) abort
    let old = s:buf_handle
    let s:buf_handle = a:handle
    return old
endfunction

function rnvimr#context#get_win_handle() abort
    return s:win_handle
endfunction

function rnvimr#context#set_win_handle(handle) abort
    let old = s:win_handle
    let s:win_handle = a:handle
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
    for bufnr in keys(filter(s:buf_cp_dict, 'empty(glob(v:val))'))
        call add(bw_list, bufnr)
    endfor
    if len(bw_list) > 0
        " execute bwipeout last buffer before leaving floating window, it may cause this issue:
        " E5601: Cannot close window, only floating window would remain
        " use timer to delay bwipeout after leaving floating window
        call timer_start(0, {-> execute('silent! bwipeout ' . join(bw_list, ' '))})
    endif
endfunction
