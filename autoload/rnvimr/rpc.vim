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
        call rpcnotify(s:host_chan_id, 'attach_file', line('w0'), a:file)
    endif
endfunction

function! rnvimr#rpc#set_host_chan_id(id) abort
    let s:host_chan_id = a:id
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
    if bufloaded(a:bufnr)
        let cur_bufnr = bufnr('%')
        execute 'noautocmd silent! buffer ' . a:bufnr
        execute 'noautocmd saveas! ' . a:target_name
        if bw_enabled
            noautocmd bwipeout #
        endif
        execute 'noautocmd silent! buffer ' . cur_bufnr
    else
        let bufname = fnamemodify(bufname(a:bufnr), ':p')
        call rnvimr#util#sync_undo(bufname, a:target_name, v:true)
        if bw_enabled
            execute 'noautocmd bwipeout ' . a:bufnr
        endif
        execute 'noautocmd badd ' . a:target_name
    endif
    noautocmd call nvim_set_current_win(rnvimr#context#winid())
    noautocmd startinsert
endfunction

function! rnvimr#rpc#edit(edit, start_line, files) abort
    let files = map(copy(a:files), 'fnameescape(v:val)')
    let picker_enabled = get(g:, 'rnvimr_enable_picker', 0)
    if picker_enabled
        close
    else
        let cur_tab = nvim_get_current_tabpage()
        let cur_win = nvim_get_current_win()
        wincmd p
    endif
    if !empty(a:edit)
        if bufname('%') != ''
            execute 'noautocmd ' . a:edit
        endif
        execute 'silent! edit ' . files[0]
    else
        if a:start_line == 0
            execute 'silent! edit ' . files[0]
            if len(files) > 1
                for f in files[1:]
                    execute 'badd ' . f
                endfor
            endif
        else
            execute 'silent! edit +normal\ ' . a:start_line . 'zt ' . files[0]
        endif
    endif
    if picker_enabled
        call rnvimr#rpc#enable_attach_file()
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
