let s:rnvimr_path = expand('<sfile>:h:h:h')
let s:ranger_cmd = get(g:, 'rnvimr_ranger_cmd', ['ranger'])
let s:os = ''

function! s:system_handler(jobid, data, event) dict abort
    if a:event ==# 'stdout' && self.ranger_host_id == -1
        let out = join(a:data)
        let host_id = str2nr(matchstr(out, 'RNVIMR_CHECKHEALTH \zs\d\+\ze RNVIMR_CHECKHEALTH'))
        if host_id > 0
            let self.ranger_host_id = host_id
        endif
    endif
endfunction

function! s:check_os() abort
    call v:lua.vim.health.start('OS')
    if has('unix')
        if has('mac') || has('macunix')
            let s:os = 'Mac'
        else
            let s:os = 'Linux'
        endif
    else
        let s:os = 'Windows'
    endif

    if s:os != 'Mac' && s:os != 'Linux'
        call v:lua.vim.health.error('Ranger is not supported for you OS')
    else
        call v:lua.vim.health.ok('Name: ' . s:os)
    endif
endfunction

function! s:check_python_ranger() abort
    call v:lua.vim.health.start('Ranger')
    let ver_info = system(s:ranger_cmd + ['--version'])
    if v:shell_error
        call v:lua.vim.health.error('Ranger not Found')
        return
    else
        let [rr_ver, py_ver] = matchlist(ver_info,
                    \ 'ranger version: \([^\n]\+\)\nPython version: \([^\n]\+\)\n')[1:2]
        let rr_ver_release = matchstr(rr_ver, '\d\+\.\d\+\.\d\+')
        if !empty(rr_ver_release) && rr_ver_release < '1.9.3'
            call v:lua.vim.health.error('Version: ' . rr_ver_release,
                        \ ['Ranger version must be greater than or equal to 1.9.3',
                        \ 'Please install Ranger properly'])
        else
            call v:lua.vim.health.ok('Version: ' . rr_ver)
        endif
    endif
    call v:lua.vim.health.start('Python')
    if py_ver[0] >= 3
        call v:lua.vim.health.ok('Version: ' . py_ver)
    else
        call v:lua.vim.health.error('Version: ' . py_ver,
                    \ ['Python version inside Ranger must be greater than 3',
                    \ 'Please install Ranger properly'])
    endif
endfunction

function! s:check_pynvim() abort
    call v:lua.vim.health.start('Pynvim')
    let pn_ver = system('python3 -c "import pynvim; v = pynvim.VERSION; ' .
                \'print(v.major, v.minor, v.patch, sep=\".\", end=\"\")"')
    if v:shell_error
        call v:lua.vim.health.error('Pynvim is not found in Python Lib')
    else
        call v:lua.vim.health.ok('Version: '. pn_ver)
    endif
endfunction

function! s:check_ueberzug() abort
    call v:lua.vim.health.start('Ueberzug (optional)')
    if s:os == 'Linux'
        let uz_out = system('python3 -c "from ueberzug import xutil; ' .
                    \ 'print(xutil.get_parent_pids.__doc__, end=\"\")"')
        let uz_err = v:shell_error
        if uz_err
            call v:lua.vim.health.warn('Ueberzug is not found in Python Lib')
        elseif uz_out == 'None'
            call v:lua.vim.health.warn('Ueberzug can not calibrate properly outside Tmux.',
                        \ 'If use Rnvimr without Tmux, please upgrade the latest version of Ueberzug')
        else
            call v:lua.vim.health.ok('Ueberzug is ready')
        endif
    else
        call v:lua.vim.health.info('Ueberzug is not support for ' . s:os)
    endif
endfunction

function! s:check_rpc() abort
    call v:lua.vim.health.start('RPC')
    try
        let $RNVIMR_CHECKHEALTH = 1
        let opts = {
                    \ 'pty': 1,
                    \ 'ranger_host_id': -1,
                    \ 'on_stdout': function('s:system_handler'),
                    \ }

        let $NVIM_LISTEN_ADDRESS = v:servername
        let confdir = s:rnvimr_path . '/ranger'
        let cmd = s:ranger_cmd + ['--confdir=' . confdir]
        let jobid = jobstart(cmd, opts)

        " jobwait doesn't work with pty option
        let count = 30
        while count > 0 && opts.ranger_host_id == -1
            sleep 100m
            let count -= 1
        endwhile

        if count == 0
            call v:lua.vim.health.error('RPC: timeout 3s')
        else
            let send = 'Give me five!'
            let rec = rpcrequest(opts.ranger_host_id, 'echo', send)
            let msg = 'RPC echo: Neovim send "' . send . '" and receive "' . rec . '"'
            if send ==# rec
                call v:lua.vim.health.ok(msg)
            else
                call v:lua.vim.health.error(msg)
            endif
        endif
        call jobstop(jobid)
    catch /.*/
        call v:lua.vim.health.error(v:exception)
    finally
        silent! unlet $RNVIMR_CHECKHEALTH
    endtry
endfunction

function! health#rnvimr#check() abort
    call s:check_os()
    call s:check_python_ranger()
    call s:check_pynvim()
    call s:check_ueberzug()
    call s:check_rpc()
endfunction
