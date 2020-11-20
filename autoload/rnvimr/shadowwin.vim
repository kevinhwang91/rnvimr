function s:shadow_existed() abort
    return exists('s:shadow_winid') && nvim_win_is_valid(s:shadow_winid)
endfunction

function! rnvimr#shadowwin#create(winblend) abort
    if s:shadow_existed()
        return
    endif

    let opts = {
                \ 'relative': 'editor',
                \ 'focusable': 0,
                \ 'width': &columns,
                \ 'height': &lines,
                \ 'col': 0,
                \ 'row': 0,
                \ 'style': 'minimal',
                \ }

    let shadow_bufnr = nvim_create_buf(0, v:true)
    call nvim_buf_set_option(shadow_bufnr, 'bufhidden', 'wipe')
    let s:shadow_winid = nvim_open_win(shadow_bufnr, 0, opts)
    call nvim_win_set_option(s:shadow_winid, 'winhighlight', 'Normal:Normal')
    call nvim_win_set_option(s:shadow_winid, 'winblend', a:winblend)
endfunction

function rnvimr#shadowwin#destroy() abort
    if !s:shadow_existed()
        return
    endif
    call nvim_win_close(s:shadow_winid, 0)
endfunction

function! rnvimr#shadowwin#reszie() abort
    if !s:shadow_existed()
        return
    endif
    call nvim_win_set_config(s:shadow_winid, {'width': &columns, 'height': &lines})
endfunction
