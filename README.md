# rnvimr

Rnvimr is a plugin to feel free to use ranger inside neovim by floating
window. Comparing other plugins about ranger just running ranger as a file
picker, this plugin uses hacking tech to do whatever you want to ranger.

**rnvimr require floating window feature, so vim is not supported.**

<p align="center">
  <img width="1080px" src="https://user-images.githubusercontent.com/17562139/74416173-b0aa8600-4e7f-11ea-83b5-31c07c384af1.gif">
</p>

> Using [vimade](https://github.com/TaDaa/vimade) to fade interactive windows.

## Requirements

1. [ranger](https://github.com/ranger/ranger)
2. [pynvim](https://github.com/neovim/pynvim)
3. [neovim](https://github.com/neovim/neovim)
4. [ueberzug](https://github.com/seebye/ueberzug) (optional, please use latest version of ranger)


## Features

* File picker
* Replace builtin Netrw to be a file explorer
* Calibrate preview images for ueberzug
* Attach file automatically when reopen ranger
* Communicate with ranger via rpc
* Adjust floating window after resize window of neovim
* Customize preset multiple layouts for floating window

## Installation

Use your plugin manager like [Vim-plug](https://github.com/junegunn/vim-plug)

Put below code in your configuration of neovim.

```vim
Plug 'kevinhwang91/rnvimr', {'do': 'make install'}
```

## Usage

Using `:RnvimrToggle` to create a new ranger process at first time.
`:RnvimrToggle` will show or hide the floating window.

Using `:RnvimrResize` to resize the floating window.

Running `:RnvimrSync` will synchronize all ranger's configuration and plugins with rnvimr.

Get more information about rnvimr, please execute `:help rnvimr` inside neovim,
because I don't want to maintain two documents with same contents :).

### Example configuration

```vim
Plug 'kevinhwang91/rnvimr', {'do': 'make install'}
" make ranger to be a file explorer
let g:rnvimr_ex_enable = 1

tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>
nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>
```

## License

The project is licensed under a BSD-3-clause license. See the [LICENSE](./LICENSE) file.
