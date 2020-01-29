let s:preset_index = 0
let s:default_layout = {
            \ 'relative': 'editor',
            \ 'width': float2nr(round(0.5 * &columns)),
            \ 'height': float2nr(round(0.5 * &lines)),
            \ 'col': float2nr(round(0.25 * &columns)),
            \ 'row': float2nr(round(0.25 * &lines)),
            \ 'style': 'minimal'
            \}
let s:default_presets = [
            \ {'width': 0.250, 'height': 0.250},
            \ {'width': 0.333, 'height': 0.333},
            \ {},
            \ {'width': 0.666, 'height': 0.666},
            \ {'width': 0.750, 'height': 0.750},
            \ {'width': 0.900, 'height': 0.900}
            \ ]

let s:layout = get(g:, 'rnvimr_layout', s:default_layout)
let s:presets = get(g:, 'rnvimr_presets', s:default_presets)

function s:get_init_index()
    let i = 0
    while i < len(s:presets)
        if empty(s:presets[i])
            let s:presets[i].width = 1.0 * s:layout.width / &columns
            let s:presets[i].height = 1.0 *s:layout.height / &lines
            let s:presets[i].col= 1.0 * s:layout.col / &columns
            let s:presets[i].row = 1.0 * s:layout.row / &lines
            break
        endif
        let i = i + 1
    endwhile
    return i == len(s:presets) ? 0 : i
endfunction

let s:init_index = s:get_init_index()

function s:process_layout_opts(opts) abort
    let opts = copy(a:opts)
    if has_key(opts, 'width')
        let t = type(opts.width)
        if t == v:t_float
            let opts.width = float2nr(opts.width * &columns)
        elseif t != v:t_number || opts.width < 1
            unlet opts.width
        endif
    endif
    if has_key(opts, 'height')
        let t = type(opts.height)
        if t == v:t_float
            let opts.height = float2nr(round(opts.height * &lines))
        elseif t != v:t_number || opts.height < 1
            unlet opts.height
        endif
    endif
    if has_key(opts, 'col')
        let t = type(opts.col)
        if t == v:t_float
            let opts.col = float2nr(round(opts.col * &columns))
        elseif t != v:t_number || opts.col < 0
            unlet opts.col
        endif
    elseif has_key(opts, 'width')
        let opts.col = float2nr(round((&columns - opts.width) / 2))
    endif
    if has_key(opts, 'row')
        let t = type(opts.row)
        if t == v:t_float
            let opts.row = float2nr(round(opts.row * &lines))
        elseif t != v:t_number || opts.row < 0
            unlet opts.row
        endif
    elseif has_key(opts, 'height')
        let opts.row = float2nr(round((&lines - opts.height) / 2))
    endif
    return opts
endfunction

function s:extend_layout(base, extend) abort
    return extend(copy(a:base), s:process_layout_opts(a:extend))
endfunction

function rnvimr#layout#get_init_layout() abort
    let s:preset_index = s:init_index
    return s:layout
endfunction

function rnvimr#layout#get_current_layout() abort
    return s:extend_layout(s:layout, s:presets[s:preset_index])
endfunction

function rnvimr#layout#get_next_layout(...) abort
    if !empty(a:000)
        let presets = []
        let cur_index = 0
        for i in uniq(copy(a:000))
            if i < len(s:presets) && i >= 0
                call add(presets, s:presets[i])
            endif
        endfor
        let cur_index = index(presets, s:presets[s:preset_index])
    else
        let presets = s:presets
        let cur_index = s:preset_index
    endif
    let next_index = cur_index < len(presets) - 1 ? cur_index + 1 : 0
    let preset = presets[next_index]
    let s:preset_index = index(s:presets, preset)
    return s:extend_layout(s:layout, preset)
endfunction
