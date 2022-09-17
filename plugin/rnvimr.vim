if exists('g:loaded_rnvimr')
    finish
endif

let g:loaded_rnvimr = 1

command! -nargs=0 RnvimrToggle call rnvimr#toggle()
command! -nargs=0 RnvimrClose call rnvimr#close()
command! -nargs=* RnvimrResize call rnvimr#resize(<args>)
command! -nargs=0 RnvimrStartBackground call rnvimr#init('', 1)

" TODO rnvimr_ex_enable was desperated.
let g:rnvimr_enable_ex = get(g:, 'rnvimr_enable_ex', 0) || get(g:, 'rnvimr_ex_enable', 0)

if get(g:, 'rnvimr_enable_ex', 0)
    augroup RnvimrFileExplorer
        autocmd!
        autocmd VimEnter * ++once silent! autocmd! FileExplorer
        autocmd VimEnter * ++once if isdirectory(expand('<amatch>')) |
                    \ bwipeout! | call rnvimr#open(expand('<amatch>')) |
                    \ endif |
                    \ execute(printf("autocmd RnvimrFileExplorer BufEnter * %s",
                    \ "call rnvimr#enter_dir(expand('<amatch>'), expand('<abuf>'))"))
    augroup END
endif
