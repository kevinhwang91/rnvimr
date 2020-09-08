let s:rnvimr_path = expand('<sfile>:h:h:h')
let s:ranger_cmd = get(g:, 'rnvimr_ranger_cmd', 'ranger')
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
    call health#report_start('OS')
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
        call health#report_error('Ranger is not supported for you OS')
    else
        call health#report_ok('Name: ' . s:os)
    endif
endfunction

function! s:check_python_ranger() abort
    call health#report_start('Ranger')
    let ver_info = system(s:ranger_cmd . ' --version')
    if v:shell_error
        call health#report_error('Ranger not Found')
        return
    else
        let [rr_ver, py_ver] = matchlist(ver_info,
                    \ 'ranger version: \([^\n]\+\)\nPython version: \([^\n]\+\)\n')[1:2]
        let rr_ver_release = matchstr(rr_ver, '\d\+\.\d\+\.\d\+')
        if !empty(rr_ver_release) && rr_ver_release < '1.9.3'
            call health#report_error('Version: ' . rr_ver_release,
                        \ ['Ranger version must be greater than or equal to 1.9.3',
                        \ 'Please install Ranger properly'])
        else
            call health#report_ok('Version: ' . rr_ver)
        endif
    endif
    call health#report_start('Python')
    if py_ver[0] >= 3
        call health#report_ok('Version: ' . py_ver)
    else
        call health#report_error('Version: ' . py_ver,
                    \ ['Python version inside Ranger must be greater than 3',
                    \ 'Please install Ranger properly'])
    endif
endfunction

function! s:check_pynvim() abort
    call health#report_start('Pynvim')
    let pn_ver = system('python3 -c "import pynvim; v = pynvim.VERSION; ' .
                \'print(v.major, v.minor, v.patch, sep=\".\", end=\"\")"')
    if v:shell_error
        call health#report_error('Pynvim is not found in Python Lib')
    else
        call health#report_ok('Version: '. pn_ver)
    endif
endfunction

function! s:check_ueberzug() abort
    call health#report_start('Ueberzug (optional)')
    if s:os == 'Linux'
        let uz_out = system('python3 -c "from ueberzug import xutil; ' .
                    \ 'print(xutil.get_parent_pids.__doc__, end=\"\")"')
        let uz_err = v:shell_error
        if uz_err
            call health#report_warn('Ueberzug is not found in Python Lib')
        elseif uz_out == 'None'
            call health#report_warn('Ueberzug can not calibrate properly outside Tmux.',
                        \ 'If use Rnvimr without Tmux, please upgrade the latest version of Ueberzug')
        else
            call health#report_ok('Ueberzug is ready')
        endif
    else
        call health#report_info('Ueberzug is not support for ' . s:os)
    endif
endfunction

function! s:check_rpc() abort
    call health#report_start('RPC')
    try
        let $RNVIMR_CHECKHEALTH = 1
        let opts = {
                    \ 'pty': 1,
                    \ 'ranger_host_id': -1,
                    \ 'on_stdout': function('s:system_handler'),
                    \ }

        let confdir = shellescape(s:rnvimr_path . '/ranger')
        let cmd = s:ranger_cmd . ' --confdir=' . confdir
        let jobid = jobstart(cmd, opts)

        " jobwait doesn't work with pty option
        let count = 30
        while count > 0 && opts.ranger_host_id == -1
            sleep 100m
            let count -= 1
        endwhile

        if count == 0
            call health#report_error('RPC: timeout 3s')
        else
            let send = 'Give me five!'
            let rec = rpcrequest(opts.ranger_host_id, 'echo', send)
            let msg = 'RPC echo: Neovim send "' . send . '" and receive "' . rec . '"'
            if send ==# rec
                call health#report_ok(msg)
            else
                call health#report_error(msg)
            endif
        endif
        call jobstop(jobid)
    catch /.*/
        call health#report_error(v:exception)
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
