let s:host_chan_id = -1
let s:attach_file_enable = 0

function s:valid_setup() abort
    if s:host_chan_id == -1
        echoerr 'ranger has not started yet.'
    endif
endfunction

function rnvimr#rpc#enable_attach_file() abort
    let s:attach_file_enable = 1
endfunction

function rnvimr#rpc#disable_attach_file() abort
    let s:attach_file_enable = 0
endfunction

function rnvimr#rpc#attach_file(file) abort
    call s:valid_setup()
    if filereadable(a:file) || isdirectory(a:file)
        call rpcnotify(s:host_chan_id, 'attach_file', a:file)
    endif
endfunction

function rnvimr#rpc#set_host_chan_id(id) abort
    let s:host_chan_id = a:id
endfunction

function rnvimr#rpc#reset_host_chan_id() abort
    let s:host_chan_id = -1
endfunction

function rnvimr#rpc#request_attach_file(file) abort
    if s:attach_file_enable == 1
        call rnvimr#rpc#attach_file(a:file)
        let s:attach_file_enable = 0
    endif
endfunction
