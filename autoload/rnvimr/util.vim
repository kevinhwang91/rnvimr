function! rnvimr#util#sync_undo(src, dst, do_bw) abort
    if !&undofile || !filereadable(a:dst)
        return
    endif
    let src = resolve(a:src)
    if &undodir == '.'
        let undo_path = printf('%s/.%s.un~', fnamemodify(src, ':p:h'), fnamemodify(src, ':t'))
    else
        let undo_path = printf('%s/%s', &undodir, fnamemodify(src, ':p:gs?/?%?'))
    endif
    if !filereadable(undo_path)
        return
    endif
    execute printf('%s edit %s', a:do_bw ? 'noautocmd' : '', a:dst)
    execute 'noautocmd silent! rundo' . fnameescape(undo_path)
    noautocmd silent! write
    if a:do_bw
        noautocmd silent! bwipeout
    endif
endfunction
