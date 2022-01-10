let s:host_chan_id = -1
let s:attach_file_enabled = 0

function! s:valid_setup() abort
    if s:host_chan_id == -1
        echoerr 'ranger has not started yet.'
        return 1
    endif
    return 0
endfunction

function! rnvimr#rpc#enable_attach_file() abort
    let s:attach_file_enabled = 1
endfunction

function! rnvimr#rpc#disable_attach_file() abort
    let s:attach_file_enabled = 0
endfunction

function! rnvimr#rpc#attach_file(file) abort
    if s:valid_setup()
        return
    endif
    if filereadable(a:file) || isdirectory(a:file)
        call rpcnotify(s:host_chan_id, 'attach_file', a:file)
    endif
endfunction

function! rnvimr#rpc#reset() abort
    let s:host_chan_id = -1
endfunction

function! rnvimr#rpc#attach_file_once(file) abort
    if s:attach_file_enabled == 1
        call rnvimr#rpc#attach_file(a:file)
        let s:attach_file_enabled = 0
    endif
endfunction

function! rnvimr#rpc#clear_image() abort
    if s:host_chan_id == -1
        return
    endif
    return rpcnotify(s:host_chan_id, 'clear_image')
endfunction

function! rnvimr#rpc#destroy() abort
    if s:host_chan_id == -1
        return
    endif
    return rpcrequest(s:host_chan_id, 'destroy')
endfunction

function! rnvimr#rpc#ranger_cmd(...) abort
    if s:valid_setup()
        return
    endif
    if !empty(a:000)
        call rpcnotify(s:host_chan_id, 'eval_cmd', a:000)
    endif
endfunction

" ranger to neovim
" =================================================================================================
function! rnvimr#rpc#host_ready(id) abort
    let s:host_chan_id = a:id
    if get(g:, 'rnvimr_draw_border', 1) && (has('mac') || has('macunix'))
        let layout = nvim_win_get_config(rnvimr#context#winid())
        let layout.width += 1
        call nvim_win_set_config(rnvimr#context#winid(), layout)
    endif
endfunction

function! rnvimr#rpc#list_buf_name_nr() abort
    let buf_dict = {}
    for buf in filter(getbufinfo({'buflisted': 1}), 'v:val.changed == 0')
        let buf_dict[buf.name] = buf.bufnr
    endfor
    return buf_dict
endfunction

function! rnvimr#rpc#do_saveas(bufnr, target_name) abort
    let bw_enabled = get(g:, 'rnvimr_enable_bw', 0)
    noautocmd wincmd p
    let cur_bufnr = bufnr('%')
    let alt_bufnr = bufnr('#')
    if bufloaded(a:bufnr)
        let wv = winsaveview()
        execute 'noautocmd silent! buffer ' . a:bufnr
        try
            execute 'noautocmd saveas! ' . a:target_name
            if bw_enabled
                noautocmd bwipeout #
                if bufloaded(alt_bufnr)
                    execute 'noautocmd silent buffer ' . alt_bufnr
                endif
            endif
        catch /.*/
        endtry
        execute 'noautocmd silent! buffer ' . cur_bufnr
        call winrestview(wv)
    else
        let bufname = fnamemodify(bufname(a:bufnr), ':p')
        call rnvimr#util#sync_undo(bufname, a:target_name, v:true)
        if bw_enabled
            execute 'noautocmd silent! bwipeout ' . a:bufnr
            if bufloaded(alt_bufnr)
                execute 'noautocmd silent buffer ' . alt_bufnr
                execute 'noautocmd silent buffer ' . cur_bufnr
            endif
        endif
        execute 'noautocmd badd ' . a:target_name
    endif
    noautocmd call nvim_set_current_win(rnvimr#context#winid())
    noautocmd startinsert
endfunction

function! rnvimr#rpc#edit(edit, files, ...) abort
    let files = map(copy(a:files), 'fnameescape(v:val)')
    let picker_enabled = empty(a:000) ? get(g:, 'rnvimr_enable_picker', 0) : a:1
    let cur_tab = nvim_get_current_tabpage()
    let cur_win = nvim_get_current_win()
    wincmd p
    let f = remove(files, 0)
    let action = bufname('%') == '' && nvim_buf_get_offset(0, 1) <= 0 || empty(a:edit) ? 'edit' : a:edit
    execute 'silent! ' . action . ' ' . f
    for f in files
        execute 'badd ' . f
    endfor
    if picker_enabled
        call rnvimr#rpc#enable_attach_file()
        call nvim_win_close(cur_win, 0)
    else
        call rnvimr#context#check_point()
        if cur_tab != nvim_get_current_tabpage()
            noautocmd call nvim_win_close(cur_win, 0)
            call rnvimr#toggle()
        else
            call nvim_set_current_win(cur_win)
        endif
    endif
    cd .
endfunction

function! rnvimr#rpc#get_window_info() abort
    try
        return nvim_win_get_config(rnvimr#context#winid())
    catch /^Vim\%((\a\+)\)\=:E5555/
        return {}
    endtry
endfunction

function! rnvimr#rpc#set_winhl(winhl) abort
    return setwinvar(rnvimr#context#winid(), '&winhighlight',
                \ getbufvar(rnvimr#context#bufnr(), a:winhl))
endfunction

function! rnvimr#rpc#notify(str, level) abort
    if exists('*nvim_notify')
        call nvim_notify(a:str, a:level, {})
    else
        echom a:str
    endif
endfunction
