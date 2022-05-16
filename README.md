# Rnvimr

Rnvimr is a NeoVim plugin that allows you to use Ranger in a floating window.

Different than other Ranger vim-plugins, Rnvimr gives you full control over Ranger.
It uses [RPC](https://neovim.io/doc/user/api.html#RPC) to communicate with Ranger.

<p align="center">
    <img width="960px" src="https://user-images.githubusercontent.com/17562139/94383438-a3be7680-0172-11eb-9f57-f3cd88aff0c0.gif">
</p>

**This plugin does not support Vim.**

## Table of contents

* [Requirements](#requirements)
* [Features](#features)
* [Installation](#installation)
  * [Dependence](#dependence)
  * [Plugin](#plugin)
  * [CheckHealth (optional)](#checkhealth-(optional))
* [Usage](#usage)
  * [Demonstration](#demonstration)
  * [Example configuration](#example-configuration)
    * [Minimal configuration](#minimal-configuration)
    * [Advanced configuration](#advanced-configuration)
* [FAQ](#faq)
* [License](#license)

## Requirements

1. [Ranger](https://github.com/ranger/ranger) (v1.9.3 or laster)
2. [Pynvim](https://github.com/neovim/pynvim)
3. [Neovim](https://github.com/neovim/neovim) 0.5 or later
4. Python3.6
5. [Ueberzug](https://github.com/seebye/ueberzug) (optional, v18.1.6 or laster)

## Features

- Replace the built-in Netrw as a default file explorer
- Calibrated preview images for ueberzug
- Attach file automatically when toggling Ranger
- Adjust floating window size automatically after resizing NeoVim
- Adjust view automatically to adapt the size of floating window
- Fully customizable layouts for floating window
- Better experience for Pager view in Ranger
- Wipe out the buffers corresponding to the files deleted by Ranger automatically
- Enhanced border in Ranger
- Synchronize the current working directory of Neovim and Ranger
- Hide the files included in gitignore
- Save Buffer information when the src files are moved from Ranger

## Installation

### Dependence

Example for [yay](https://github.com/Jguer/yay) in ArchLinux and
[pip](https://pip.pypa.io/en/stable/) in other \*unix distributions:

```sh
# ArchLinux install all requirements is extremely convenient
yay -S ranger python-pynvim ueberzug

# pip

# macOS users please install ranger by `pip3 ranger-fm` instead of `brew install ranger`
# There're some issues about installation, such as https://github.com/ranger/ranger/issues/1214
# Please refer to the issues of ranger for more details
pip3 install ranger-fm pynvim

# ueberzug is not supported in macOS because it depends on X11
pip3 install ueberzug
```

> Ueberzug is optional

### Plugin

Install Rnvimr with your favorite plugin manager! Example for [Vim-plug](https://github.com/junegunn/vim-plug):

```vim
Plug 'kevinhwang91/rnvimr'
```

### CheckHealth (optional)

Run `nvim +'checkhealth rnvimr'` in shell. If everything is OK, it will output like these:

```log
health#rnvimr#check
========================================================================
## OS
  - OK: Name: Linux

## Ranger
  - OK: Version: ranger-master

## Python
  - OK: Version: 3.8.3 (default, May 17 2020, 18:15:42) [GCC 10.1.0]

## Pynvim
  - OK: Version: 0.4.1

## Ueberzug (optional)
  - OK: Ueberzug is ready

## RPC
  - OK: RPC echo: Neovim send "Give me five!" and receive "Give me five!"
```

## Usage

Using `:RnvimrToggle` to create a Ranger process, and if one exists,
`:RnvimrToggle` simply shows or hides the floating window.

Using `:RnvimrResize` to cycle the preset layouts.

Pressing `Enter` to open a file in Ranger.

Rnvimr also supports `ctrl-t`/`ctrl-x`/`ctrl-v` key bindings that allow you to
open up a file in a new tab, a new horizontal split, or in a new vertical split.

Pressing `q` in Ranger simply hides the floating window.
Ranger will attach the file of the current buffer in the next toggle event.

Pressing `yw` in Ranger will emit Ranger's cwd to Neovim's, `gw` will jump to Neovim's cwd.

### Demonstration

<details>
    <summary>Hide the files included in gitignore</summary>
    <p align="center">
        <img src="https://user-images.githubusercontent.com/17562139/86036499-8e04bc80-ba70-11ea-9f89-dac26795b7ec.png">
    </p>
</details>
<details>
    <summary>Save buffers information (undo) when the src files are moved from Ranger</summary>
    <p align="center">
        <img width="960px" src="https://user-images.githubusercontent.com/17562139/86033825-23518200-ba6c-11ea-88d6-914d8d8f1f96.gif">
    </p>
</details>

### Example configuration

#### Minimal configuration

```vim
Plug 'kevinhwang91/rnvimr'

tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>
nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>
```

#### Advanced configuration

```vim
Plug 'kevinhwang91/rnvimr'

" Make Ranger replace Netrw and be the file explorer
let g:rnvimr_enable_ex = 1

" Make Ranger to be hidden after picking a file
let g:rnvimr_enable_picker = 1

" Replace `$EDITOR` candidate with this command to open the selected file
let g:rnvimr_edit_cmd = 'drop'

" Disable a border for floating window
let g:rnvimr_draw_border = 0

" Hide the files included in gitignore
let g:rnvimr_hide_gitignore = 1

" Change the border's color
let g:rnvimr_border_attr = {'fg': 14, 'bg': -1}

" Make Neovim wipe the buffers corresponding to the files deleted by Ranger
let g:rnvimr_enable_bw = 1

" Add a shadow window, value is equal to 100 will disable shadow
let g:rnvimr_shadow_winblend = 70

" Draw border with both
let g:rnvimr_ranger_cmd = ['ranger', '--cmd=set draw_borders both']

" Link CursorLine into RnvimrNormal highlight in the Floating window
highlight link RnvimrNormal CursorLine

nnoremap <silent> <M-o> :RnvimrToggle<CR>
tnoremap <silent> <M-o> <C-\><C-n>:RnvimrToggle<CR>

" Resize floating window by all preset layouts
tnoremap <silent> <M-i> <C-\><C-n>:RnvimrResize<CR>

" Resize floating window by special preset layouts
tnoremap <silent> <M-l> <C-\><C-n>:RnvimrResize 1,8,9,11,5<CR>

" Resize floating window by single preset layout
tnoremap <silent> <M-y> <C-\><C-n>:RnvimrResize 6<CR>

" Map Rnvimr action
let g:rnvimr_action = {
            \ '<C-t>': 'NvimEdit tabedit',
            \ '<C-x>': 'NvimEdit split',
            \ '<C-v>': 'NvimEdit vsplit',
            \ 'gw': 'JumpNvimCwd',
            \ 'yw': 'EmitRangerCwd'
            \ }

" Add views for Ranger to adapt the size of floating window
let g:rnvimr_ranger_views = [
            \ {'minwidth': 90, 'ratio': []},
            \ {'minwidth': 50, 'maxwidth': 89, 'ratio': [1,1]},
            \ {'maxwidth': 49, 'ratio': [1]}
            \ ]

" Customize the initial layout
let g:rnvimr_layout = {
            \ 'relative': 'editor',
            \ 'width': float2nr(round(0.7 * &columns)),
            \ 'height': float2nr(round(0.7 * &lines)),
            \ 'col': float2nr(round(0.15 * &columns)),
            \ 'row': float2nr(round(0.15 * &lines)),
            \ 'style': 'minimal'
            \ }

" Customize multiple preset layouts
" '{}' represents the initial layout
let g:rnvimr_presets = [
            \ {'width': 0.600, 'height': 0.600},
            \ {},
            \ {'width': 0.800, 'height': 0.800},
            \ {'width': 0.950, 'height': 0.950},
            \ {'width': 0.500, 'height': 0.500, 'col': 0, 'row': 0},
            \ {'width': 0.500, 'height': 0.500, 'col': 0, 'row': 0.5},
            \ {'width': 0.500, 'height': 0.500, 'col': 0.5, 'row': 0},
            \ {'width': 0.500, 'height': 0.500, 'col': 0.5, 'row': 0.5},
            \ {'width': 0.500, 'height': 1.000, 'col': 0, 'row': 0},
            \ {'width': 0.500, 'height': 1.000, 'col': 0.5, 'row': 0},
            \ {'width': 1.000, 'height': 0.500, 'col': 0, 'row': 0},
            \ {'width': 1.000, 'height': 0.500, 'col': 0, 'row': 0.5}
            \ ]

" Fullscreen for initial layout
" let g:rnvimr_layout = {
"            \ 'relative': 'editor',
"            \ 'width': &columns,
"            \ 'height': &lines - 2,
"            \ 'col': 0,
"            \ 'row': 0,
"            \ 'style': 'minimal'
"            \ }
"
" Only use initial preset layout
" let g:rnvimr_presets = [{}]

```

For more information, please refer to [:help rnvimr](./doc/rnvimr.txt),
because I don't want to maintain two documents with the same contents :).

## FAQ

Q: Couldn't open some special types of files by using `Enter` or `l` in Ranger.

A: Please follow the below steps to solve this issue:

1. The behavior of opening the file in Ranger depends on `rifle.conf`.
   Press `r` to make sure that the `${VISUAL:-$EDITOR} -- "$@"` is the best candidate in Ranger.
2. If the case 1 is false, change the code in `rifle.conf` like that:

<!-- markdownlint-disable MD013 -->

```diff
-!mime ^text, label editor, ext xml|json|csv|tex|py|pl|rb|js|sh|php = ${VISUAL:-$EDITOR} -- "$@"
+!mime ^text, label editor, ext xml|json|csv|tex|py|pl|rb|js|sh|php|your_file_type = ${VISUAL:-$EDITOR} -- "$@"
```

<!-- markdownlint-enable MD013 -->

Q: CheckHealth says RPC timeout.

A: Install [Dependence](#Dependence) first,
run ex command`:echo $NVIM_LISTEN_ADDRESS` to
confirm that the message output is in a format like this `/tmp/nvimIYj484/0` or a tcp format
`address:port`, Rnvimr needs this environment variable.

Q: How can I go back to the previous directory in Ranger after attaching a new file?

A: Press `H` in Ranger, mean go back to the last history directory.

Q: How can I use Ranger default configuration (vanilla)?

A: Write `let g:rnvimr_vanilla = 1` to your vim configuration.

Q: `let g:rnvimr_enable_ex = 1` can't work as expected.

A: Turn off the option of other plugins (like `let g:NERDTreeHijackNetrw = 0` which is used in
NERDTree) or uninstall the conflicting plugins.

Q: In MacOS, I must press `<ctrl-v>` twice to split window vertically.

A: Please refer to [#71](https://github.com/kevinhwang91/rnvimr/issues/71) and use `rnvimr_action`
variable to remap `<ctrl-v>` as a workaround for the issue.

## License

The project is licensed under a BSD-3-clause license. See [LICENSE](./LICENSE) file for details.
