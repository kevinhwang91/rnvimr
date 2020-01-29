# rnvimr

Rnvimr is a plugin to feel free to use ranger inside neovim by floating
window. Comparing other plugins about ranger just running ranger as a file
picker, this plugin uses hacking tech to do whatever you want to ranger.

*rnvimr require floating window feature, so vim is not supported.*

## Requirements

1. [ranger](https://github.com/ranger/ranger)
2. [pynvim](https://github.com/neovim/pynvim)
3. [neovim](https://github.com/neovim/neovim)
4. [ueberzug](https://github.com/seebye/ueberzug) (optional)


## Features

* File picker
* Replace builtin Netrw
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

Open a new floating window and run a ranger process by using `:RnvimrToggle`.

You can run `:RnvimrResize` to resize floating window.

Running `:RnvimrSync` will synchronize all ranger's configuration and plugins with rnvimr.

Get more information about rnvimr, please execute `:help rnvimr` inside neovim,
because I don't want to maintain two documents with same contents :).

## License

The project is licensed under a BSD-3-clause license. See the [LICENSE](./LICENSE) file.
