let s:rnvimr_path = expand('<sfile>:h:h')
let s:confdir = s:rnvimr_path . '/ranger'
let s:default_ranger_cmd = ['ranger']
let s:default_action = {
            \ '<C-t>': 'NvimEdit tabedit',
            \ '<C-x>': 'NvimEdit split',
            \ '<C-v>': 'NvimEdit vsplit',
            \ '<C-o>': 'NvimEdit drop',
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
            \ 'edit_cmd': get(g:, 'rnvimr_edit_cmd', 'edit'),
            \ 'hide_gitignore': get(g:, 'rnvimr_hide_gitignore', 0),
            \ 'draw_border': g:rnvimr_draw_border,
            \ 'border_attr': get(g:, 'rnvimr_border_attr', {}),
            \ 'views': get(g:, 'rnvimr_ranger_views', []),
            \ }

let s:channel = -1

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
    call s:setup_winhl()
    startinsert
    doautocmd RnvimrTerm TermEnter
    if has('nvim-0.8.0')
        call chansend(s:channel, 0z00)
    endif
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

function! s:create_ranger(cmd, env, is_background) abort
    let init_layout = rnvimr#layout#get_init_layout()
    if get(g:, 'rnvimr_draw_border', 1) && (has('mac') || has('macunix'))
        let init_layout.width -= 1
    endif
    call rnvimr#context#bufnr(nvim_create_buf(v:false, v:true))
    if a:is_background
        noa let winid = nvim_open_win(rnvimr#context#bufnr(), v:true, init_layout)
    else
        let winid = nvim_open_win(rnvimr#context#bufnr(), v:true, init_layout)
    endif
    call rnvimr#context#winid(winid)
    let s:channel = termopen(a:cmd, {'on_exit': function('s:on_exit'), 'env': a:env})
    setfiletype rnvimr
    " TODO
    " double type <C-\> make ranger crash, this is ranger issue.
    tnoremap <buffer> <C-\><C-\> <Nop>
    call s:setup_winhl()
    if !a:is_background
        startinsert
    endif
    augroup RnvimrTerm
        autocmd!
        autocmd VimResized <buffer> call s:redraw_win()
        autocmd VimLeavePre * call rnvimr#rpc#destroy()
        if get(g:, 'rnvimr_enable_bw', 0)
            autocmd TermEnter,WinEnter <buffer> call rnvimr#context#check_point()
            autocmd WinClosed <buffer> call rnvimr#context#buf_wipe()
        endif
        if s:shadow_winblend < 100 && s:shadow_winblend >= 0
            autocmd TermEnter,WinEnter <buffer> call rnvimr#shadowwin#create(s:shadow_winblend)
            autocmd WinLeave <buffer> call rnvimr#shadowwin#destroy()
            autocmd VimResized <buffer> call rnvimr#shadowwin#reszie()
        endif
    augroup END
    if a:is_background
        call rnvimr#rpc#enable_attach_file()
        noa call nvim_win_close(winid, 0)
    endif
endfunction

function! s:defer_check_dir(path, bufnr) abort
    if isdirectory(a:path) && !&diff && a:bufnr == nvim_get_current_buf()
        let alter_bufnr = bufnr(0)
        if alter_bufnr > 0 && alter_bufnr != a:bufnr
            buffer #
        else
            enew
        endif
        bwipeout #
        call rnvimr#open(a:path)
    end
endfunction

function! rnvimr#enter_dir(path, bufnr) abort
    if bufnr(a:path) == a:bufnr && isdirectory(a:path) && !&diff
        " git submodule opened by `:Git difftool -y` for vim-fugitive is treated as directory,
        " but vim-fugitive couldn't set &diff before BufEnter event, let us check it later:)
        call timer_start(0, {-> call('s:defer_check_dir', [a:path, a:bufnr])})
    endif
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
    let isdir = isdirectory(a:path)
    if rnvimr#context#bufnr() != -1
        if filereadable(a:path) || isdir
            call rnvimr#rpc#attach_file(a:path)
            call rnvimr#rpc#disable_attach_file()
        endif
        call rnvimr#toggle()
    else
        call rnvimr#init(a:path)
    endif
    if isdir && rnvimr#layout#get_current_index() != get(g:, 'rnvimr_layout_ex_index', 0)
        call rnvimr#resize(g:rnvimr_layout_ex_index)
    endif
endfunction

function! rnvimr#enable_mouse_support() abort
    function s:set_mouse_with_rnvimr() abort
    let n_mouse = &mouse
    augroup RnvimrMouse
        autocmd!
        autocmd FileType rnvimr call <SID>set_mouse_with_rnvimr()
    augroup end

    if match(n_mouse, '[a|h|n]') >= 0
        augroup RnvimrMouse
            autocmd TermEnter,WinEnter <buffer> call nvim_set_option('mouse', '')
            execute printf("autocmd WinLeave <buffer> call nvim_set_option('mouse', '%s')", n_mouse)
        augroup END
    endif

  if system('tmux display -p "#{mouse}"')[0]
  augroup RnvimrMouse
      autocmd TermEnter,WinEnter <buffer> call system('tmux set mouse off')
      autocmd WinLeave <buffer> call system('tmux set mouse on')
  augroup END
  endif

endfunction

augroup RnvimrMouse
    autocmd FileType rnvimr call <SID>set_mouse_with_rnvimr()
augroup END
endfunction

" a:1 select_file
" a:2 is_background
function! rnvimr#init(...) abort
    if rnvimr#context#bufnr() != -1
        return
    endif
    let $NVIM_LISTEN_ADDRESS = v:servername
    let select_file = empty(get(a:000, 0, '')) ? expand('%:p') : a:1
    let is_background = get(a:000, 1, 0)
    let confdir = s:confdir
    " https://github.com/kevinhwang91/rnvimr/issues/80
    if filewritable(s:confdir) == 0
        let confdir = fnamemodify(tempname(), ':h') . '/rnvimr'
        if empty(glob(confdir))
            let sh_conf = shellescape(confdir . '/')
            call system('cp -r ' . shellescape(s:confdir) . ' ' . sh_conf . ' && chmod +w -R ' . sh_conf)
        endif
    endif
    let attach_cmd = 'AttachFile ' . select_file
    let ranger_cmd = get(g:, 'rnvimr_ranger_cmd', s:default_ranger_cmd)
    if type(ranger_cmd) != v:t_list
        echoerr '`g:rnvimr_ranger_cmd` has changed, please use a list instead of string'
    endif
    let env = {}
    if get(g:, 'rnvimr_vanilla', 0)
        let env.RNVIMR_VANILLA = 1
    endif
    let urc_path = get(g:, 'rnvimr_urc_path', v:null)
    if !empty(urc_path)
        let env.RNVIMR_URC_PATH = urc_path
    endif
    rnvimr#enable_mouse_support()

    let cmd = ranger_cmd + ['--confdir='. confdir, '--cmd='. attach_cmd]
    call s:create_ranger(cmd, env, is_background)
endfunction
