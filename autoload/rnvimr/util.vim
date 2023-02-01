function! rnvimr#util#sync_undo(src, dst, do_bw) abort
    if !&undofile || !filereadable(a:dst)
        return
    endif
    let undo_path = undofile(a:src)
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
