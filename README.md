# Rnvimr

Rnvimr is a NeoVim plugin that allows you to use Ranger in a floating window.

Different than other Ranger vim-plugins, Rnvimr gives you full control over Ranger. It uses [RPC](https://neovim.io/doc/user/api.html#RPC) to communicate with Ranger.

**Since Rnvimr requires RPC, this plugin does not support Vim for now.**

<p align="center">
  <img width="1080px" src="https://user-images.githubusercontent.com/17562139/74416173-b0aa8600-4e7f-11ea-83b5-31c07c384af1.gif">
</p>

> [vimade](https://github.com/TaDaa/vimade) was used to fade interactive windows.

## Requirements

1. [Ranger](https://github.com/ranger/ranger)
2. [Pynvim](https://github.com/neovim/pynvim)
3. [Neovim](https://github.com/neovim/neovim)
4. Python3
5. [Ueberzug](https://github.com/seebye/ueberzug) (optional, Ranger is required at least [b58954](https://github.com/Ranger/Ranger/commit/b58954d4258bc204c38f635e5209e6c1e2bce743), if you don't use Tmux, Ueberzug is required at least [d86eeb](https://github.com/seebye/ueberzug/commit/d86eeb303b9468226884425853472287a794d9dd))

## Features

- Replaces the built-in Netrw as a default file explorer
- Calibrated preview images for ueberzug
- Attach file automatically when toggling Ranger
- Runs [RPC](https://neovim.io/doc/user/api.html#RPC) inside Ranger to communicate with NeoVim
- Automatically adjusts floating window after resizing NeoVim
- Fully customizable layouts for floating window
- Better experience for Pager view in Ranger
- Automatically wipe the buffers corresponding to the files deleted by Ranger

## Installation

### Requirements

Example for [yay](https://github.com/Jguer/yay) in ArchLinux and [pip](https://pip.pypa.io/en/stable/) in other *unix distributions:

```sh
# ueberzug is optional

# ArchLinux install all requirements is extreme convenient
yay -S ranger-git python-pynvim python-ueberzug-git

# pip
pip3 install ranger-fm pynvim
# If you use tmux, run `pip3 ueberzug` directly to install ueberzug, otherwise install by source code
git clone https://github.com/seebye/ueberzug.git && cd ueberzug
pip3 install .
```

### Plugin

Install Rnvimr with your favorite plugin manager! Example for [Vim-plug](https://github.com/junegunn/vim-plug):

```vim
Plug 'kevinhwang91/rnvimr', {'do': 'make sync'}
```

> If you want Rnvimr to use the default (vanilla) Ranger configuration, please using `make install` instead of `make sync`.

### CheckHealth (optional)

Run `nvim +'checkhealth rnvimr'` in shell. If everything is OK, it will output like these:

```vim
health#rnvimr#check
========================================================================
## OS
  - OK: OS: Linux

## Ranger
  - OK: Version: ranger-master

## Python
  - OK: Version: 3.8.2 (default, Apr  8 2020, 14:31:25) [GCC 9.3.0]

## Pynvim
  - OK: Version: 0.4.1

## Ueberzug (optional)
  - OK: Ueberzug is ready

## RPC
  - OK: Install Rnvimr lib for checkhealth successfully
  - OK: RPC: Neovim send "Give me five!" and receive "Give me five!"
  - OK: Clean Rnvimr lib checkhealth successfully
```

## Usage

Use `:RnvimrToggle` to create a Ranger process, and if one exists, `:RnvimrToggle` simply shows or hides the floating window.

Use `:RnvimrResize` to cycle the preset layouts.

`:RnvimrSync` will synchronize your personal Ranger configuration and plugins with Rnvimr this time.

**Note:** if your Ranger config changes, you will have to run `:RnvimrSync` in order to use your updated Ranger configuration with Rnvimr

`Enter` to open a file in Ranger. Rnvimr also supports `CTRL-T`/`CTRL-X`/`CTRL-V` key bindings that allow you to open up file in a new tab, a new horizontal split, or in a new vertical split.

Pressing `q` in Ranger simply hides the floating window. Ranger will attach the file of the current buffer in the next toggle event.

Synchronize the scroll line of pager view with Neovim:

<p align="center">
  <img width="960px" src="https://user-images.githubusercontent.com/17562139/79363617-b5241580-7f7a-11ea-9332-bd865dd2cf1e.gif">
</p>

### Example configuration

#### Minimal configuration

```vim
" Synchronize all Ranger's configuration and plugins with Rnvimr
Plug 'kevinhwang91/rnvimr', {'do': 'make sync'}

tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>
nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>
```

#### Advanced configuration

```vim
" Synchronize all Ranger's configuration and plugins with Rnvimr
Plug 'kevinhwang91/rnvimr', {'do': 'make sync'}

" Make Ranger replace netrw and be the file explorer
let g:rnvimr_ex_enable = 1

" Make Ranger to be hidden after picking a file
let g:rnvimr_pick_enable = 1

" Disable a border for floating window
let g:rnvimr_draw_border = 0

" Make Neovim to wipe the buffers corresponding to the files deleted by Ranger
let g:rnvimr_bw_enable = 1

" Set up only two columns in miller mode and draw border with separators
let g:rnvimr_ranger_cmd = 'ranger --cmd="set column_ratios 1,1"
            \ --cmd="set draw_borders separators"'

" highlight text in Floating window
highlight NormalFloat ctermfg=0 ctermbg=16 guibg=#2b3038

nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>

" Resize floating window by all preset layouts
tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>

" Resize floating window by special preset layouts
tnoremap <silent> <M-l> <C-\><C-n>:RnvimrResize 1,8,9,11,5<CR>

" Resize floating window by single preset layout
tnoremap <silent> <M-y> <C-\><C-n>:RnvimrResize 6<CR>

" Customize the initial layout
let g:rnvimr_layout = { 'relative': 'editor',
            \ 'width': float2nr(round(0.6 * &columns)),
            \ 'height': float2nr(round(0.6 * &lines)),
            \ 'col': float2nr(round(0.2 * &columns)),
            \ 'row': float2nr(round(0.2 * &lines)),
            \ 'style': 'minimal' }

" Customize multiple preset layouts
" '{}' represents the initial layout
let g:rnvimr_presets = [
            \ {},
            \ {'width': 0.700, 'height': 0.700},
            \ {'width': 0.800, 'height': 0.800},
            \ {'width': 0.950, 'height': 0.950}
            \ {'width': 0.500, 'height': 0.500, 'col': 0, 'row': 0},
            \ {'width': 0.500, 'height': 0.500, 'col': 0, 'row': 0.5},
            \ {'width': 0.500, 'height': 0.500, 'col': 0.5, 'row': 0},
            \ {'width': 0.500, 'height': 0.500, 'col': 0.5, 'row': 0.5},
            \ {'width': 0.500, 'height': 1.000, 'col': 0, 'row': 0},
            \ {'width': 0.500, 'height': 1.000, 'col': 0.5, 'row': 0},
            \ {'width': 1.000, 'height': 0.500, 'col': 0, 'row': 0},
            \ {'width': 1.000, 'height': 0.500, 'col': 0, 'row': 0.5}]
```

For more information, please refer to [:help rnvimr](./doc/rnvimr.txt),
because I don't want to maintain two documents with the same contents :).

## FAQ

Q: Couldn't open some special type of files by using `Enter` or `l` in Ranger.

A: Please follow below steps to solve this issue:

1. The behavior of openning the file in Ranger depends on `rifle.conf`. Press `r` to make sure that the `${VISUAL:-$EDITOR} -- "$@"` is the best candidate in Ranger.
2. If the case 1 is false, change the code in `rifle.conf` like that:

```diff
-!mime ^text, label editor, ext xml|json|csv|tex|py|pl|rb|js|sh|php = ${VISUAL:-$EDITOR} -- "$@"
+!mime ^text, label editor, ext xml|json|csv|tex|py|pl|rb|js|sh|php|your_file_type = ${VISUAL:-$EDITOR} -- "$@"
```

3. execute`:RnvimrSync` to synchronize the `rifle.conf` just modified with Rnvimr.

Q: This plugin doesn't work for me.

A: Install [Requirements](#Requirements) first, if you use Mac, you should install Ranger by `pip install ranger-fm` instead of `brew install ranger` because the Ranger installed by brew still using Python2.

## License

The project is licensed under a BSD-3-clause license. See [LICENSE](./LICENSE) file for details.
