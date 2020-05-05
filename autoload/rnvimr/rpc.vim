let s:host_chan_id = -1
let s:attach_file_enable = 0

function! s:valid_setup() abort
    if s:host_chan_id == -1
        echoerr 'ranger has not started yet.'
    endif
endfunction

function! rnvimr#rpc#enable_attach_file() abort
    let s:attach_file_enable = 1
endfunction

function! rnvimr#rpc#disable_attach_file() abort
    let s:attach_file_enable = 0
endfunction

function! rnvimr#rpc#buf_checkpoint() abort
    let s:buf_cp_dict = {}
    for buf in filter(getbufinfo({'buflisted': 1}),
                \'v:val.changed == 0 && !empty(glob(v:val.name))')
        let s:buf_cp_dict[buf.bufnr] = buf.name
    endfor
endfunction

function! rnvimr#rpc#buf_wipe() abort
    let bw_list = []
    for bufnr in keys(filter(s:buf_cp_dict, 'empty(glob(v:val))'))
        call add(bw_list, bufnr)
    endfor
    if len(bw_list) > 0
        " execute bwipeout last buffer before leaving floating window, it may cause this issue:
        " E5601: Cannot close window, only floating window would remain
        " use timer to delay bwipeout after leaving floating window
        call timer_start(0, {-> execute('bwipeout ' . join(bw_list, ' '))})
    endif
endfunction

function! rnvimr#rpc#attach_file(file) abort
    call s:valid_setup()
    if filereadable(a:file) || isdirectory(a:file)
        call rpcnotify(s:host_chan_id, 'attach_file', line('w0'), a:file)
    endif
endfunction

function! rnvimr#rpc#set_host_chan_id(id) abort
    let s:host_chan_id = a:id
endfunction

function! rnvimr#rpc#reset_host_chan_id() abort
    let s:host_chan_id = -1
endfunction

function! rnvimr#rpc#attach_file_once(file) abort
    if s:attach_file_enable == 1
        call rnvimr#rpc#attach_file(a:file)
        let s:attach_file_enable = 0
    endif
endfunction
