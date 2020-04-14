if exists('g:loaded_rnvimr')
    finish
endif

let g:loaded_rnvimr = 1

command! -nargs=0 RnvimrToggle call rnvimr#toggle()
command! -nargs=* RnvimrResize call rnvimr#resize(<args>)
command! -nargs=0 RnvimrSync call rnvimr#sync_ranger()

if get(g:, 'rnvimr_ex_enable', 0)
    augroup RnvimrFileExplorer
        autocmd VimEnter * ++once silent! autocmd! FileExplorer
        autocmd VimEnter * ++once if isdirectory(expand('<amatch>'))|
                    \ bwipeout! | call rnvimr#open(expand('<amatch>')) | endif
        autocmd BufEnter * if isdirectory(expand('<amatch>')) && v:vim_did_enter |
                    \ bwipeout! | call rnvimr#open(expand('<amatch>')) | endif
    augroup END
endif
