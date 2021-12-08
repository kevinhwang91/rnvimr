local M = {}

local api = vim.api
local fn = vim.fn
local uv = vim.loop

local host_chan_id
local attach_file_enabled

local function valid_setup()
    if host_chan_id == -1 then
        api.nvim_err_writeln('range has not started yet.')
        return false
    end
    return true
end

function M.enable_attach_file()
    info('enable_attach_file')
    attach_file_enabled = true
end

function M.disable_attach_file()
    info('disable_attach_file')
    attach_file_enabled = false
end

function M.attach_file(file)
    info('attach_file', file)
    if not valid_setup() then
        return
    end

    local st = uv.fs_stat(file)
    local stt = st and st.type
    if stt and stt == 'directory' or stt == 'file' then
        fn.rpcnotify(host_chan_id, 'attach_file', fn.line('w0'), file)
    end
end

function M.reset()
    info('reset')
    host_chan_id = -1
end

function M.attach_file_once(file)
    info('attach_file_once', file)
    if attach_file_enabled then
        M.attach_file(file)
        attach_file_enabled = false
    end
end

function M.clear_image()
    info('clear_image')
    if host_chan_id == -1 then
        return
    end
    fn.rpcnotify(host_chan_id, 'clear_image')
end

function M.destroy()
    info('destroy')
    if host_chan_id == -1 then
        return
    end
    return fn.rpcrequest(host_chan_id, 'destroy')
end

function M.ranger_cmd(...)
    info('ranger_cmd', ...)
    if not valid_setup() then
        return
    end

    local argc = select('#', ...)
    if argc > 0 then
        fn.rpcnotify(host_chan_id, 'eval_cmd', ...)
    end
end

function M.host_ready(id)
    info('host_ready', id)
    host_chan_id = id
end

local function init()
    host_chan_id = -1
    attach_file_enabled = false
end

init()

return M
