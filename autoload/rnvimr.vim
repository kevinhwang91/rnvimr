let s:rnvimr_path = expand('<sfile>:h:h')
let s:confdir = s:rnvimr_path . '/ranger'
let s:default_ranger_cmd = 'ranger'
let s:default_action = {
            \ '<C-t>': 'NvimEdit tabedit',
            \ '<C-x>': 'NvimEdit split',
            \ '<C-v>': 'NvimEdit vsplit',
            \ 'gw': 'JumpNvimCwd',
            \ 'yw': 'EmitRangerCwd',
            \ }
let s:shadow_winblend = get(g:, 'rnvimr_shadow_winblend', 100)

" TODO rnvimr_picker_enable and rnvimr_bw_enable were deprecated.
let g:rnvimr_enable_picker = get(g:, 'rnvimr_enable_picker', 0)
            \ || get(g:, 'rnvimr_pick_enable', 0)
let g:rnvimr_enable_bw = get(g:, 'rnvimr_enable_bw', 0)
            \ || get(g:, 'rnvimr_bw_enable', 0)

let g:rnvimr_draw_border = get(g:, 'rnvimr_draw_border', 1)

let g:rnvimr_ranger_init = {
            \ 'action': get(g:, 'rnvimr_action', s:default_action),
            \ 'hide_gitignore': get(g:, 'rnvimr_hide_gitignore', 0),
            \ 'urc_path': get(g:, 'rnvimr_urc_path', v:null),
            \ 'draw_border': g:rnvimr_draw_border,
            \ 'border_attr': get(g:, 'rnvimr_border_attr', {}),
            \ 'views': get(g:, 'rnvimr_ranger_views', []),
            \ 'vanilla': get(g:, 'rnvimr_vanilla', 0)
            \ }

highlight default link RnvimrNormal NormalFloat
highlight default link RnvimrCurses Normal

function! s:redraw_win() abort
    let layout = rnvimr#layout#get_current_layout()
    call nvim_win_set_config(rnvimr#context#winid(), layout)
    " TODO
    " clear screen is not working inside VimResized event
    " add a timer to implement redraw is a dirty way, please fix
    call timer_start(0, {-> execute('mode')})
endfunction

function! s:reopen_win() abort
    let layout = rnvimr#layout#get_current_layout()
    call rnvimr#context#winid(nvim_open_win(rnvimr#context#bufnr(), v:true, layout))
    startinsert
endfunction

function! s:on_exit(job_id, data, event) abort
    if a:data == 0
        bdelete!
    endif
    call rnvimr#context#bufnr(-1)
    call rnvimr#rpc#reset()
endfunction

function! s:setup_winhl() abort
    let buf_hd = rnvimr#context#bufnr()
    call setbufvar(buf_hd, 'normal_winhl', 'Normal:RnvimrNormal')
    call setbufvar(buf_hd, 'curses_winhl', 'Normal:RnvimrCurses')
    if g:rnvimr_draw_border
        let default_winhl = getbufvar(buf_hd, 'curses_winhl')
    else
        let default_winhl = getbufvar(buf_hd, 'normal_winhl')
    endif
    call setwinvar(rnvimr#context#winid(), '&winhighlight', default_winhl)
endfunction

function! s:create_ranger(cmd) abort
    let init_layout = rnvimr#layout#get_init_layout()
    call rnvimr#context#bufnr(nvim_create_buf(v:false, v:true))
    call rnvimr#context#winid(
                \ nvim_open_win(rnvimr#context#bufnr(), v:true, init_layout))
    call termopen(a:cmd, {'on_exit': function('s:on_exit')})
    setfiletype rnvimr
    call s:setup_winhl()
    startinsert
endfunction

function! rnvimr#resize(...) abort
    let win_hd = rnvimr#context#winid()
    if !nvim_win_is_valid(win_hd) ||
                \ nvim_get_current_win() != win_hd
        return
    endif
    let layout = call(function('rnvimr#layout#get_next_layout'), a:000)
    call nvim_win_set_config(win_hd, layout)
    startinsert
endfunction

function! rnvimr#toggle() abort
    let win_hd = rnvimr#context#winid()
    if rnvimr#context#bufnr() != -1
        if win_hd != -1 && nvim_win_is_valid(win_hd)
            if nvim_get_current_win() == win_hd
                call nvim_win_close(win_hd, 0)
                call rnvimr#rpc#clear_image()
            else
                call nvim_set_current_win(win_hd)
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
    if rnvimr#context#bufnr() != -1
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
        autocmd VimLeavePre * call rnvimr#rpc#destroy()
        if get(g:, 'rnvimr_enable_bw', 0)
            autocmd TermEnter,WinEnter <buffer> call rnvimr#context#check_point()
            autocmd WinLeave <buffer> call rnvimr#context#buf_wipe()
        endif
        if s:shadow_winblend < 100 && s:shadow_winblend >= 0
            autocmd TermEnter,WinEnter <buffer> call rnvimr#shadowwin#create(s:shadow_winblend)
            autocmd WinLeave <buffer> call rnvimr#shadowwin#destroy()
            autocmd VimResized <buffer> call rnvimr#shadowwin#reszie()
        endif
    augroup END
endfunction
