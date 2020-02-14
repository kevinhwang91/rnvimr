# rnvimr

Rnvimr is a plugin to feel free to use ranger inside neovim by floating
window. 

Comparing other plugins about ranger just running ranger as a file
picker, this plugin uses hacking tech to do whatever you want to ranger, such as running rpc inside ranger to communicate with neovim.


**rnvimr require floating window feature, so vim is not supported.**

<p align="center">
  <img width="1080px" src="https://user-images.githubusercontent.com/17562139/74416173-b0aa8600-4e7f-11ea-83b5-31c07c384af1.gif">
</p>

> Using [vimade](https://github.com/TaDaa/vimade) to fade interactive windows.

## Requirements

1. [ranger](https://github.com/ranger/ranger)
2. [pynvim](https://github.com/neovim/pynvim)
3. [neovim](https://github.com/neovim/neovim)
4. [ueberzug](https://github.com/seebye/ueberzug) (optional, update ranger since [b58954](https://github.com/ranger/ranger/commit/b58954d4258bc204c38f635e5209e6c1e2bce743))


## Features

* Replace builtin Netrw to be a file explorer
* Calibrate preview images for ueberzug
* Attach file automatically when toggling ranger again
* Run rpc inside ranger to communicate with neovim
* Adjust floating window after resizing window of neovim
* Customize multiple preset layouts for floating window

## Installation

Use your plugin manager like [Vim-plug](https://github.com/junegunn/vim-plug)

Put below code in your configuration of neovim.

```vim
Plug 'kevinhwang91/rnvimr', {'do': 'make install'}
```

## Usage

Using `:RnvimrToggle` to create a ranger process at first time.
`:RnvimrToggle` will show or hide the floating window.

Using `:RnvimrResize` to resize the floating window.

Running `:RnvimrSync` will synchronize all ranger's configuration and plugins with rnvimr.

### Example configuration

#### Minimal configuration
```vim
Plug 'kevinhwang91/rnvimr', {'do': 'make install'}

tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>
nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>
```

#### Advanced configuration
```vim
" Synchronize all ranger's configuration and plugins with rnvimr
Plug 'kevinhwang91/rnvimr', {'do': 'make sync'}

" make ranger to replace netrw to be a file explorer
let g:rnvimr_ex_enable = 1

nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>

" Resize floating window by all preset layouts
tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>

" Resize floating window by special preset layouts
tnoremap <silent> <M-l> <C-\><C-n>:RnvimrResize 1,8,9,13,11,5<CR>

" Resize floating window by single preset layouts
tnoremap <silent> <M-y> <C-\><C-n>:RnvimrResize 6<CR>

" Customize initial layout
let g:rnvimr_layout = { 'relative': 'editor',
            \ 'width': float2nr(round(0.5 * &columns)),
            \ 'height': float2nr(round(0.5 * &lines)),
            \ 'col': float2nr(round(0.25 * &columns)),
            \ 'row': float2nr(round(0.25 * &lines)),
            \ 'style': 'minimal' }

" Customize multiple preset layouts
" '{}' represents initial layout
let g:rnvimr_presets = [
            \ {'width': 0.250, 'height': 0.250},
            \ {'width': 0.333, 'height': 0.333},
            \ {},
            \ {'width': 0.666, 'height': 0.666},
            \ {'width': 0.750, 'height': 0.750},
            \ {'width': 0.900, 'height': 0.900},
            \ {'width': 0.500, 'height': 0.500, 'col': 0, 'row': 0},
            \ {'width': 0.500, 'height': 0.500, 'col': 0, 'row': 0.5},
            \ {'width': 0.500, 'height': 0.500, 'col': 0.5, 'row': 0},
            \ {'width': 0.500, 'height': 0.500, 'col': 0.5, 'row': 0.5},
            \ {'width': 0.500, 'height': 1.000, 'col': 0, 'row': 0},
            \ {'width': 0.500, 'height': 1.000, 'col': 0.5, 'row': 0},
            \ {'width': 1.000, 'height': 0.500, 'col': 0, 'row': 0},
            \ {'width': 1.000, 'height': 0.500, 'col': 0, 'row': 0.5}]
```

Get more information about rnvimr, please execute `:help rnvimr` inside neovim,
because I don't want to maintain two documents with same contents :).

## License

The project is licensed under a BSD-3-clause license. See the [LICENSE](./LICENSE) file.

