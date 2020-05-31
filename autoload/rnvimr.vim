let s:rnvimr_path = expand('<sfile>:h:h')
let s:editor = s:rnvimr_path . '/bin/editor.py'
let s:confdir = s:rnvimr_path . '/ranger'
let s:default_ranger_cmd = 'ranger'
let s:default_action = {
            \ '<C-t>': 'NvimEdit tabedit',
            \ '<C-x>': 'NvimEdit split',
            \ '<C-v>': 'NvimEdit vsplit',
            \ 'gw': 'JumpNvimCwd',
            \ 'yw': 'EmitRangerCwd'
            \}

let g:rnvimr_action = get(g:, 'rnvimr_action', s:default_action)
let g:rnvimr_draw_border = get(g:, 'rnvimr_draw_border', 1)
let g:rnvimr_pick_enable = get(g:, 'rnvimr_pick_enable', 0)

highlight default link RnvimrNormal NormalFloat
highlight default link RnvimrCurses Normal

function! s:redraw_win() abort
    let layout = rnvimr#layout#get_current_layout()
    call nvim_win_set_config(s:win_handle, layout)
    " TODO
    " clear screen is not working inside VimResized event
    " add a timer to implement redraw is a dirty way, please fix
    call timer_start(0, {-> execute('mode')})
endfunction

function! s:reopen_win() abort
    let layout = rnvimr#layout#get_current_layout()
    let s:win_handle = nvim_open_win(s:buf_handle, v:true, layout)
    startinsert
endfunction

function! s:on_exit(job_id, data, event) abort
    if a:data == 0
        bdelete!
    endif
    unlet s:buf_handle
    call rnvimr#rpc#reset()
endfunction

function! s:setup_winhl() abort
    call setbufvar(s:buf_handle, 'normal_winhl', 'Normal:RnvimrNormal')
    call setbufvar(s:buf_handle, 'curses_winhl', 'Normal:RnvimrCurses')
    if g:rnvimr_draw_border
        let default_winhl = getbufvar(s:buf_handle, 'curses_winhl')
    else
        let default_winhl = getbufvar(s:buf_handle, 'normal_winhl')
    endif
    call setwinvar(s:win_handle, '&winhighlight', default_winhl)
endfunction

function! s:create_ranger(cmd) abort
    let init_layout = rnvimr#layout#get_init_layout()
    let s:buf_handle = nvim_create_buf(v:false, v:true)
    let s:win_handle = nvim_open_win(s:buf_handle, v:true, init_layout)
    call termopen(a:cmd, {'on_exit': function('s:on_exit')})
    setfiletype rnvimr
    call s:setup_winhl()
    startinsert
endfunction

function! rnvimr#set_winhl(winhl) abort
    call setwinvar(s:win_handle, '&winhighlight', getbufvar(s:buf_handle, a:winhl))
endfunction

function! rnvimr#resize(...) abort
    if !nvim_win_is_valid(s:win_handle) || nvim_get_current_win() != s:win_handle
        return
    endif
    let layout = call(function('rnvimr#layout#get_next_layout'), a:000)
    call nvim_win_set_config(s:win_handle, layout)
    startinsert
endfunction

function! rnvimr#toggle() abort
    if exists('s:buf_handle')
        if exists('s:win_handle') && nvim_win_is_valid(s:win_handle)
            if nvim_get_current_win() == s:win_handle
                call nvim_win_close(s:win_handle, 0)
            else
                call nvim_set_current_win(s:win_handle)
                startinsert
            endif
        else
            call rnvimr#rpc#attach_file_once(expand('%:p'))
            call s:reopen_win()
        endif
    else
        call rnvimr#init()
    endif
endfunction

function! rnvimr#open(path) abort
    if exists('s:buf_handle')
        if filereadable(a:path) || isdirectory(a:path)
            call rnvimr#rpc#attach_file(a:path)
            call rnvimr#rpc#disable_attach_file()
        endif
        call rnvimr#toggle()
    else
        call rnvimr#init(a:path)
    endif
endfunction

function! rnvimr#init(...) abort
    let select_file = empty(a:000) ? expand('%:p') : a:1
    let confdir = shellescape(s:confdir)
    let attach_cmd = shellescape('AttachFile ' . line('w0') . ' ' . select_file)
    let ranger_cmd = get(g:, 'rnvimr_ranger_cmd', s:default_ranger_cmd)
    let cmd = ranger_cmd . ' --confdir=' . confdir . ' --cmd=' . attach_cmd
    call s:create_ranger(cmd)
    augroup RnvimrTerm
        autocmd!
        autocmd VimResized <buffer> call s:redraw_win()
        autocmd VimLeavePre * call rnvimr#rpc#destory()
        if get(g:, 'rnvimr_bw_enable', 0)
            autocmd TermEnter,WinEnter <buffer> call rnvimr#rpc#buf_checkpoint()
            autocmd WinLeave <buffer> call rnvimr#rpc#buf_wipe()
        endif
    augroup END
endfunction

function! rnvimr#sync_ranger() abort
    let sync_path = get(g:, 'rnvimr_sync_path')
    let make_cmd = sync_path == 0 ? 'make sync' : 'make RANGER_CONFIG='
                \ . shellescape(sync_path) . 'sync'
    let msg = system('cd ' . s:rnvimr_path . ';' . make_cmd)
    if v:shell_error
        echoerr msg
    endif
endfunction
