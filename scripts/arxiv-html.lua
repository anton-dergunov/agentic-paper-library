-- Pandoc filter for arXiv's LaTeXML HTML (used by html-to-markdown.py).
--
-- arXiv wraps nearly every element in <div>/<span> with ids and classes.
-- Unwrapping them lets pandoc keep raw HTML enabled, which it needs for one
-- thing: tables too complex for a GitHub markdown table (merged cells, several
-- paragraphs in a cell) are written as HTML <table>s instead of being dropped
-- for a "[TABLE]" placeholder. Everything else stays plain markdown.

function Div(el)
  return el.content
end

-- Math is rendered by KaTeX (VS Code's preview, Obsidian), which covers most
-- of LaTeX math but not everything papers use. The TeX arXiv keeps for each
-- equation is the author's source, including the paper's own macros (\rank,
-- \defeq) and LaTeX layout commands. Normalise it so KaTeX can draw it.

-- Every control sequence KaTeX supports, generated from KaTeX itself, and
-- those among them it refuses inside a text argument (\times, \pm, \mathbin).
local SUPPORTED, MATH_ONLY = {}, {}
do
  local dir = (PANDOC_SCRIPT_FILE or ""):match("(.*/)") or "./"
  for line in io.lines(dir .. "katex-commands.txt") do
    local name, flag = line:match("^(%a+)%s*(%a*)")
    if name then
      SUPPORTED[name] = true
      if flag == "math" then MATH_ONLY[name] = true end
    end
  end
end

-- Commands KaTeX lacks that have a close equivalent it has.
local EQUIVALENT = {
  mathds = "\\mathbb",        -- dsfont's indicator 1
  mathbbm = "\\mathbb",       -- bbm's indicator 1
  textsc = "\\text",          -- small caps: keep the text, lose the caps
  mbox = "\\text",
  nicefrac = "\\tfrac",
  textless = "<",
  textgreater = ">",
  textvisiblespace = "\\text{␣}",
  texttildelow = "\\text{\\textasciitilde}",
  -- KaTeX draws it, but it is a symbol, so the generated command list lacks it.
  textasciicircum = "\\textasciicircum",
  -- Cross-references and citations: keep the label or key as text.
  ref = "\\text", eqref = "\\text", cref = "\\text", Cref = "\\text",
  autoref = "\\text", cite = "\\text", citep = "\\text", citet = "\\text",
  -- The LaTeX kernel's math-mode section and paragraph signs.
  mathsection = "\\S", mathparagraph = "\\P",
  -- KaTeX has these, MathJax (GitHub, Obsidian) does not.
  argmax = "\\operatorname*{arg\\,max}", argmin = "\\operatorname*{arg\\,min}",
  -- The physics package's \qty only sizes the brackets after it.
  qty = "",
}

-- Commands whose braced argument is text, not math.
local TEXT_CMDS = {
  text = true, textrm = true, textit = true, textbf = true, textsf = true,
  texttt = true, textup = true, textnormal = true, textsc = true, mbox = true,
  hbox = true, emph = true,
}
-- Commands with a text argument that is not their first: \raisebox{len}{text}.
local TEXT_ARG = { raisebox = 2 }

-- LaTeXML's internals, which no renderer knows: dropped, with their braced
-- arguments where they take any. \@@bibref{..}{key}{..}{..} keeps the key.
local INTERNAL = {
  ["@add@centering"] = 0, ["@pc@lb"] = 0, ["@@citephrase"] = 1, ["@@bibref"] = 4,
}

-- LaTeX layout commands that mean nothing in a rendered equation, with the
-- length or number some of them take. \hskip is the exception: it separates
-- two expressions on one line ("a=1,\hskip 9.24994pt b=2"), so it is kept as
-- the \hspace KaTeX understands.
local LAYOUT = {
  vskip = true, hskip = true, penalty = true, hfil = true, hfill = true,
  indent = true, noindent = true, nobreak = true, allowbreak = true,
  centering = true,
}
local UNITS = {
  pt = true, em = true, ex = true, mu = true, bp = true, cm = true, mm = true,
  ["in"] = true, pc = true, dd = true, cc = true, sp = true,
}

-- The end of a TeX length starting at i ("-3.5pt", "1fil"), or nil.
local function length_end(t, i)
  local num = t:match("^[%-+]?%s*%d*%.?%d+", i)
  if not num then return nil end
  local j = i + #num
  j = j + #(t:match("^%s*", j))
  local fil = t:match("^fil+", j)
  if fil then return j + #fil end
  if UNITS[t:sub(j, j + 1)] then return j + 2 end
  return i + #num  -- a bare number (\penalty 10000)
end

local function strip_layout(t)
  local out, i = {}, 1
  while true do
    local s, e, name = t:find("\\(%a+)", i)
    if not s then break end
    table.insert(out, t:sub(i, s - 1))
    if not LAYOUT[name] then
      table.insert(out, t:sub(s, e))
      i = e + 1
    else
      local j = e + 1 + #(t:match("^%s*", e + 1))
      local len_end = length_end(t, j)
      local len = len_end and t:sub(j, len_end - 1):gsub("%s", "") or nil
      j = len_end or j
      -- "\penalty\ ": the control space stood where the number goes.
      if name == "penalty" and not len_end and t:sub(j, j + 1) == "\\ " then j = j + 2 end
      -- Glue: "plus 1fil minus 2pt".
      while true do
        local k = j + #(t:match("^%s*", j))
        local kw = t:match("^plus", k) or t:match("^minus", k)
        local glue_end = kw and length_end(t, k + #kw + #(t:match("^%s*", k + #kw)))
        if not glue_end then break end
        j = glue_end
      end
      if name == "hskip" and len and UNITS[len:sub(-2)] then
        table.insert(out, "\\hspace{" .. len .. "}")
      end
      i = j
    end
  end
  table.insert(out, t:sub(i))
  return table.concat(out)
end

-- One pass over the TeX that knows, at each point, whether it is in math or in
-- a text argument (\text{...}, the box of \raisebox), and fixes what depends
-- on it:
--
-- * A "$" inside the TeX would end the markdown math span early. Inside text
--   ("\text{bo$n$}") it switches to math, so write it as \( ... \); in math
--   ("0.769$\pm$0.162") it is redundant, so drop it.
-- * A command KaTeX lacks: use its equivalent if there is one; otherwise it is
--   the paper's own macro (\rank, \defeq), shown as its name upright:
--   \operatorname in math, \textrm in text, where \operatorname is not allowed.
-- * A command KaTeX has only in math, met in text ("\text{\times}", siunitx's
--   output): written with its arguments inside \( ... \).
-- * "_" in text (a label, "\text{eq:chain_rule}") is escaped.
local function rewrite_commands(t)
  local out = {}
  local modes = { "math" }        -- mode of each open brace group
  local pending_text = 0          -- which coming "{" opens a text argument (1 = the next)
  local pending_depth = 0         -- the depth those groups open at
  local dollar_open = false       -- inside a $...$ or \(...\) that began in text mode
  local dollar_depth = 0          -- the depth it began at; a text group inside it is text again
  local wrap = nil                -- depth at which a \( opened for a math-only command
  local i, n = 1, #t
  local function mode()
    if dollar_open and #modes == dollar_depth then return "math" end
    return modes[#modes]
  end
  local function close_wrap()
    if wrap then
      table.insert(out, "\\)")
      wrap = nil
    end
  end
  -- The braced group starting at i (after spaces), as (content, index after it).
  local function group(at)
    local s = at + #(t:match("^%s*", at))
    if t:sub(s, s) ~= "{" then return nil, at end
    local depth, j = 0, s
    while j <= n do
      local ch = t:sub(j, j)
      if ch == "\\" then j = j + 1
      elseif ch == "{" then depth = depth + 1
      elseif ch == "}" then
        depth = depth - 1
        if depth == 0 then return t:sub(s + 1, j - 1), j + 1 end
      end
      j = j + 1
    end
    return nil, at
  end
  while i <= n do
    local c = t:sub(i, i)
    -- The arguments of a wrapped command are the groups (and scripts) right
    -- after it; anything else ends the \( ... \).
    if wrap == #modes and not c:match("[{^_]") then close_wrap() end
    local internal = c == "\\" and t:match("^[%a@]*@[%a@]*", i + 1)
    if internal then
      -- One not listed (\lx@scalerel@obj) is dropped too; its arguments stay.
      i = i + 1 + #internal
      local key
      for k = 1, INTERNAL[internal] or 0 do
        local content, after = group(i)
        if not content then break end
        if k == 2 then key = content end
        i = after
      end
      if internal == "@@bibref" and key then
        key = key:gsub("_", "\\_")
        table.insert(out, mode() == "text" and key or "\\text{" .. key .. "}")
      end
    elseif c == "\\" then
      local name = t:match("^%a+", i + 1)
      if name then
        i = i + 1 + #name
        local cmd = "\\" .. name
        if EQUIVALENT[name] then
          cmd = EQUIVALENT[name]
        elseif not SUPPORTED[name] then
          if mode() == "text" then
            cmd = "\\textrm{" .. name .. "}"
          else
            cmd = "\\operatorname{" .. name .. "}"
            -- As a bare script ("U^\T") it has to be one group.
            if out[#out] == "^" or out[#out] == "_" then cmd = "{" .. cmd .. "}" end
          end
        elseif MATH_ONLY[name] and mode() == "text" then
          table.insert(out, "\\(")
          wrap = #modes
        end
        local base = cmd:match("^\\(%a+)$")
        pending_text = base and (TEXT_CMDS[base] and 1 or TEXT_ARG[base]) or 0
        pending_depth = #modes
        -- \text[citep]{...}: LaTeXML's optional argument means nothing here.
        if base and TEXT_CMDS[base] then
          local opt = t:match("^%[%a*%]", i)
          if opt then i = i + #opt end
        end
        table.insert(out, cmd)
      else
        -- "\\", "\{", "\$", "\ " and the like: copy both characters. A
        -- discretionary hyphen or product and the italic correction mean
        -- nothing to KaTeX.
        local two = t:sub(i, i + 1)
        if two == "\\(" and mode() == "text" then
          dollar_open, dollar_depth = true, #modes
        elseif two == "\\)" and dollar_open and #modes == dollar_depth then
          dollar_open = false
        end
        if two ~= "\\-" and two ~= "\\/" and two ~= "\\*" then table.insert(out, two) end
        i = i + 2
      end
    elseif c == "{" then
      local counted = pending_text > 0 and pending_depth == #modes
      table.insert(modes, counted and pending_text == 1 and "text" or (wrap and "math" or mode()))
      if counted then pending_text = pending_text - 1 end
      table.insert(out, c)
      i = i + 1
    elseif c == "}" then
      if wrap and wrap >= #modes then close_wrap() end
      if #modes > 1 then table.remove(modes) end
      table.insert(out, c)
      i = i + 1
    elseif c == "$" then
      if modes[#modes] == "text" and not wrap then
        table.insert(out, dollar_open and "\\)" or "\\(")
        dollar_open, dollar_depth = not dollar_open, #modes
      end
      i = i + 1
    elseif c == "_" and mode() == "text" and not wrap then
      table.insert(out, "\\_")
      i = i + 1
    else
      if not c:match("%s") and pending_depth == #modes then pending_text = 0 end
      table.insert(out, c)
      i = i + 1
    end
  end
  close_wrap()
  return table.concat(out)
end

-- siunitx numbers arrive as their unrounded input with digit groups
-- ("0.769\,142\,111\,540\,03" where the PDF prints 0.77). Join the groups; a
-- number with nine or more decimals is such raw input, so round it to four.
local function join_digit_groups(t)
  -- \num{2294} with a group separator LaTeXML did not resolve: "2true294".
  local joined_true
  repeat
    t, joined_true = t:gsub("(%d)true(%d%d%d)%f[%D]", "%1%2")
  until joined_true == 0
  return (t:gsub("%d[%d.]*\\,[%d\\,]*%d", function(number)
    local groups, valid = {}, true
    for group in (number .. "\\,"):gmatch("(.-)\\,") do
      table.insert(groups, group)
    end
    -- Decimal groups follow ".ddd" and may end short; integer groups
    -- ("10\,000") are all three digits. Anything else ("1\,2") is not a number.
    local decimal = groups[1]:match("^%d+%.%d%d%d$") ~= nil
    valid = decimal or groups[1]:match("^%d%d?%d?$") ~= nil
    for k = 2, #groups do
      if decimal and k == #groups then
        valid = valid and groups[k]:match("^%d%d?%d?$") ~= nil
      else
        valid = valid and groups[k]:match("^%d%d%d$") ~= nil
      end
    end
    if not valid then return number end
    local joined = table.concat(groups)
    local decimals = joined:match("%.(%d+)$")
    if decimals and #decimals >= 9 then
      joined = string.format("%.4f", tonumber(joined))
    end
    return joined
  end))
end

-- mleftright's \mleft( ... \mright) arrives as
-- "\mathopen{}\mathclose{{\left( ... }}\right)", with \left and \right in
-- different groups, which KaTeX refuses. Take the wrapper off.
local function unwrap_mleft(t)
  local open = "\\mathopen{}\\mathclose{{\\left"
  local from = 1
  while true do
    local s, e = t:find(open, from, true)
    if not s then return t end
    -- The "}}" that closes the wrapper's two groups.
    local depth, j, close = 2, e + 1, nil
    while j <= #t do
      local c = t:sub(j, j)
      if c == "\\" then j = j + 1
      elseif c == "{" then depth = depth + 1
      elseif c == "}" then
        depth = depth - 1
        if depth == 0 then close = j break end
      end
      j = j + 1
    end
    if close and t:sub(close - 1, close) == "}}" and t:match("^%s*\\right", close + 1) then
      t = t:sub(1, s - 1) .. "\\left" .. t:sub(e + 1, close - 2) .. t:sub(close + 1)
      from = s
    else
      from = e + 1
    end
  end
end

-- The braced group at i, as (content, index after it), or nil.
local function braced(t, i)
  if t:sub(i, i) ~= "{" then return nil end
  local depth, j = 0, i
  while j <= #t do
    local c = t:sub(j, j)
    if c == "\\" then j = j + 1
    elseif c == "{" then depth = depth + 1
    elseif c == "}" then
      depth = depth - 1
      if depth == 0 then return t:sub(i + 1, j - 1), j + 1 end
    end
    j = j + 1
  end
  return nil
end

-- \mathchoice{display}{text}{script}{scriptscript} picks a rendering by math
-- style; a paper's own "\sim" raised in a box arrives as four copies of
-- "\vbox{\hbox{$\scriptstyle\sim$}}". Keep the text-style one, out of its boxes.
local function unwrap_mathchoice(t)
  local from = 1
  while true do
    local s, e = t:find("\\mathchoice", from, true)
    if not s then return t end
    local groups, i = {}, e + 1
    for _ = 1, 4 do
      local content, after = braced(t, i + #(t:match("^%s*", i)))
      if not content then break end
      table.insert(groups, content)
      i = after
    end
    if #groups == 4 then
      local pick = groups[2]
      local inner = pick:match("^%s*\\vbox%s*{%s*\\hbox%s*{%s*%$(.-)%$%s*}%s*}%s*$")
      t = t:sub(1, s - 1) .. "{" .. (inner or pick) .. "}" .. t:sub(i)
      from = s
    else
      from = e + 1
    end
  end
end

local function hex(x)
  return string.format("%02X", math.floor(tonumber(x) * 255 + 0.5))
end

local function normalise_math(t)
  -- \color[rgb]{1,0,0} (xcolor's model syntax) -> \color{#FF0000}
  t = t:gsub("\\(%a*color)%[rgb%]{%s*([%d.]+)%s*,%s*([%d.]+)%s*,%s*([%d.]+)%s*}",
    function(cmd, r, g, b) return "\\" .. cmd .. "{#" .. hex(r) .. hex(g) .. hex(b) .. "}" end)
  t = t:gsub("\\(%a*color)%[named%]", "\\%1")
  t = t:gsub("\\lx@sectionsign", "\\S ")
  t = t:gsub("\\addcontentsline%b{}%b{}%b{}", "")
  t = t:gsub("\\begin{array}%[%]", "\\begin{array}")
  -- "@{...}" in an array's columns ("{rcl@{\qquad}l}") sets the space between
  -- two columns, which KaTeX does not take.
  t = t:gsub("(\\begin{array})(%b{})", function(b, cols)
    if not cols:find("@", 1, true) then return nil end
    return b .. cols:gsub("@%b{}", "")
  end)
  -- mathtools' multlined, which KaTeX lacks: lines one under another.
  t = t:gsub("\\(%a+){multlined}", "\\%1{gathered}")
  -- KaTeX draws split only in a display equation, and an equation row's
  -- cells are inline until they are joined; aligned is drawn the same.
  t = t:gsub("\\(%a+){split}", "\\%1{aligned}")
  -- A bare \mod ("$\mod$" between two words) has no argument for KaTeX.
  t = t:gsub("\\mod%s*$", "\\operatorname{mod}")
  -- The physics package's \order{n} is O(n).
  t = t:gsub("\\order%s*(%b{})", function(arg) return "\\mathcal{O}(" .. arg:sub(2, -2) .. ")" end)
  -- A \par that came along inside a macro's argument.
  t = t:gsub("\\par%f[%A]", "")
  -- \scalebox{0.7}{$\pm$}: the size goes, what was scaled stays.
  t = t:gsub("\\scalebox%s*%b{}", ""):gsub("\\resizebox%s*%b{}%s*%b{}", "")
  t = unwrap_mleft(t)
  t = unwrap_mathchoice(t)
  return rewrite_commands(strip_layout(join_digit_groups(t)))
end

function Math(m)
  m.text = normalise_math(m.text)
  if m.mathtype == "InlineMath" then
    -- A lone currency sign set as math: "$\$$" reads as the start of a
    -- display equation.
    if m.text:match("^%s*\\%$%s*$") then return pandoc.Str("$") end
    -- "pass\^{}k" set as text around an empty accent: the caret itself.
    if m.text:match("^%s*\\hat%s*{%s*}%s*$") then return pandoc.Str("^") end
    -- A control space at the end would leave "\$", an escaped dollar.
    m.text = m.text:gsub("^(.-[^\\])\\%s+$", "%1")
    -- A matrix written over several lines: inline math stays on one.
    m.text = m.text:gsub("%s*\n%s*", " ")
  end
  return m
end

-- esvect's \vv{n} arrives as two pieces: the arrow's expanded internals
-- (\montraita ... \fldr), which LaTeXML could not parse, then the argument.
local function is_vv_arrow(el)
  return el.t == "Math" and el.text:find("montrait", 1, true) and el.text:find("fldr", 1, true)
end

-- Three things that go wrong when math is written next to other text:
-- LaTeXML sometimes splits one expression into adjacent pieces, and "$a$$b$"
-- would open a display equation, so merge them; a currency sign before math
-- ("\$" then "$15$") becomes "\$$15$", so move the sign into the math; and a
-- \vv arrow is put back on its argument as \vec.
function Inlines(inlines)
  local out = pandoc.List()
  local vv = false
  for _, el in ipairs(inlines) do
    local prev = out[#out]
    if is_vv_arrow(el) then
      vv = true
      goto continue
    end
    if vv then
      if el.t == "Space" or el.t == "SoftBreak" or (el.t == "Str" and el.text == "") then goto continue end
      vv = false
      if el.t == "Math" then
        el.text = "\\vec{" .. el.text:gsub("^\\textstyle%s*", "") .. "}"
      end
    end
    if el.t == "Math" and el.mathtype == "InlineMath" and prev then
      if prev.t == "Math" and prev.mathtype == "InlineMath" then
        prev.text = prev.text .. " " .. el.text
        goto continue
      end
      if prev.t == "Str" and prev.text:sub(-1) == "$" then
        prev.text = prev.text:sub(1, -2)
        if prev.text == "" then out:remove() end
        el.text = "\\$" .. el.text
        -- "$x$" before the sign would now touch this one: "$x$$\$y$".
        prev = out[#out]
        if prev and prev.t == "Math" and prev.mathtype == "InlineMath" then
          prev.text = prev.text .. " " .. el.text
          goto continue
        end
      end
    end
    out:insert(el)
    ::continue::
  end
  return out
end

-- A title broken over two lines ("Terminal-Bench:<br>Benchmarking ...") would be
-- written as a setext heading with a hard break in it.
function Header(el)
  el.content = el.content:walk({
    LineBreak = function() return pandoc.Space() end,
    -- A heading set in bold is still only a heading.
    Strong = function(s) return s.content end,
    Underline = function(s) return s.content end,
  })
  return el
end

-- \textbf, \textit and \underline arrive as spans. In a table they are what
-- the paper claims (the best result, the significant one), in running text
-- the run-in headings and the terms being defined.
local FONTS = {
  { "ltx_font_bold", "Strong" }, { "ltx_font_italic", "Emph" },
  { "ltx_underline", "Underline" }, { "ltx_framed_underline", "Underline" },
}

-- A space, or the no-break spaces LaTeXML pads a cell's text with.
local function is_space(el)
  return el.t == "Space" or el.t == "SoftBreak" or (el.t == "Str" and not el.text:gsub("\u{a0}", ""):match("%S"))
end

-- A word without the padding at one end ("^" or "$"). The no-break space is
-- matched as its two bytes together and the spaces are listed: a character
-- class takes each byte alone, and %s takes the byte 0xA0 in some locales,
-- either of which cuts "†" or "±" in half.
local function trim_padding(text, at)
  local n
  repeat
    if at == "^" then
      text, n = text:gsub("^\u{a0}", "")
      if n == 0 then text, n = text:gsub("^[ \t\r\n]+", "") end
    else
      text, n = text:gsub("\u{a0}$", "")
      if n == 0 then text, n = text:gsub("[ \t\r\n]+$", "") end
    end
  until n == 0
  return text
end

function Span(el)
  local content = el.content
  -- A caption's "Table 7:" is matched as plain text (caption-numbers.py),
  -- also when the style sets its two words in bold one by one.
  if el.classes:includes("ltx_tag") then
    local function plain(inner) return inner.content end
    return pandoc.Inlines(content):walk({ Strong = plain, Emph = plain, Underline = plain })
  end
  if not pandoc.utils.stringify(content):match("%S") then return content end
  -- Shading the converter kept (mark_shading in html-to-markdown.py).
  if el.classes:includes("mark") then
    return pandoc.List({ pandoc.RawInline("html", "<mark>") }) .. content
      .. pandoc.List({ pandoc.RawInline("html", "</mark>") })
  end
  for _, font in ipairs(FONTS) do
    if el.classes:includes(font[1]) then
      local kind = font[2]
      -- Bold inside bold is still bold, and the spaces at either end stay outside the marks.
      content = pandoc.Inlines(content):walk({ [kind] = function(inner) return inner.content end })
      local before, after = pandoc.List(), pandoc.List()
      while #content > 0 and is_space(content[1]) do before:insert(content:remove(1)) end
      while #content > 0 and is_space(content[#content]) do after:insert(1, content:remove()) end
      -- The padding also comes joined to the first and the last word.
      local first, last = content[1], content[#content]
      if first and first.t == "Str" then first.text = trim_padding(first.text, "^") end
      if last and last.t == "Str" then last.text = trim_padding(last.text, "$") end
      content = before .. pandoc.List({ pandoc[kind](content) }) .. after
    end
  end
  return content
end

-- A float's label set in bold ("**Table 7:** Results") is the label all the same.
local function plain_label(el)
  local first = el.content[1]
  if first and first.t == "Strong"
      and pandoc.utils.stringify(first):match("^%a+%.?%s[%w.]+[:.]?%s*$") then
    el.content:remove(1)
    for k, inline in ipairs(first.content) do el.content:insert(k, inline) end
    return el
  end
end

Para = plain_label
Plain = plain_label

-- With raw HTML on, any link or image carrying an id or class is written as an
-- HTML tag; without the attributes it stays a markdown link.
--
-- LaTeXML gives every cross-reference a hover title, the path to its target
-- ("Table 8 ‣ 4.2 Results ‣ 4 Experiments ‣ <the paper's title>"): a twelfth
-- of a paper's text, repeated at each reference. Only the float it names is
-- kept, for caption-numbers.py, which removes it once the captions are numbered.
function Link(el)
  el.attr = pandoc.Attr()
  if el.target:sub(1, 1) == "#" then
    local title = el.title:gsub("\u{a0}", " ")
    el.title = title:match("^Table [%w.]+") or title:match("^Figure [%w.]+") or ""
  end
  return el
end

-- arXiv's alt text is mostly a placeholder ("Refer to caption",
-- "[Uncaptioned image]"), which goes; an author's own description of the
-- figure (\Description in ACM papers) stays.
local PLACEHOLDER_ALT = { ["Refer to caption"] = true, ["[Uncaptioned image]"] = true, image = true }

function Image(el)
  el.attr = pandoc.Attr()
  if PLACEHOLDER_ALT[pandoc.utils.stringify(el.caption)] then
    el.caption = {}
  end
  return el
end

-- Likewise a figure would be written as <figure>: emit its content, then the
-- caption as a plain paragraph ("Table 1: ..."), which is how it read before.
function Figure(fig)
  local out = pandoc.List(fig.content)
  local caption = fig.caption.long
  if #caption > 0 then
    out:extend(caption)
  end
  return out
end

local function is_equation(tbl)
  for _, c in ipairs({ "ltx_equation", "ltx_equationgroup", "ltx_eqn_table" }) do
    if tbl.classes:includes(c) then return true end
  end
  return false
end

-- Text that goes inside \text{...} in an equation.
local function tex_text(s)
  return (s:gsub("[\\{}#$%%&_^~]", function(c)
    if c == "\\" then return "\\textbackslash{}" end
    if c == "^" or c == "~" then return "\\" .. c .. "{}" end
    return "\\" .. c
  end))
end

-- A cell's content in reading order, as a list of {math=...} and {text=...}.
local function cell_parts(blocks)
  local parts = {}
  local function add_text(s)
    local last = parts[#parts]
    if last and last.text then last.text = last.text .. s else table.insert(parts, { text = s }) end
  end
  local inlines
  local function blocks_of(bs)
    for _, b in ipairs(bs) do
      if b.t == "Plain" or b.t == "Para" then inlines(b.content)
      elseif b.t == "Div" then blocks_of(b.content)
      else add_text(pandoc.utils.stringify(b)) end
    end
  end
  inlines = function(ils)
    for _, el in ipairs(ils) do
      if el.t == "Math" then table.insert(parts, { math = el.text })
      elseif el.t == "Str" or el.t == "Code" then add_text(el.text)
      elseif el.t == "Space" or el.t == "SoftBreak" or el.t == "LineBreak" then add_text(" ")
      elseif el.content and type(el.content) ~= "string" then inlines(el.content)
      end
    end
  end
  blocks_of(blocks)
  return parts
end

-- Whether a cell's TeX continues the previous cell ("=b" after "a").
local function continues(tex)
  tex = tex:gsub("^\\displaystyle", ""):gsub("^[%s{}]+", "")
  if tex:match("^[=<>+%-:,;]") then return true end
  local cmd = tex:match("^\\(%a+)")
  return cmd ~= nil and (cmd:match("eq$") or cmd:match("arrow$") or ({
    le = true, ge = true, leqslant = true, geqslant = true, lesssim = true, gtrsim = true,
    prec = true, succ = true, mid = true, models = true, vdash = true, approx = true, sim = true, simeq = true, equiv = true, propto = true,
    ["in"] = true, notin = true, to = true, mapsto = true, subset = true, subseteq = true,
    ll = true, gg = true, cong = true, cdot = true, times = true, pm = true, mp = true,
    coloneqq = true, triangleq = true, defeq = true, vdots = true, ldots = true, cdots = true,
  })[cmd]) or false
end

-- LaTeXML lays out numbered equations as tables whose cells hold the math and
-- the equation number. Turn each row into one display equation, with \tag{n}:
-- an aligned "a" & "= b" pair is joined, separate equations on one row
-- ("I = ..., s = ..., y = ...") are spaced apart, and text in a cell ("output",
-- a "# comment") is kept as \text. A row that is prose (\intertext, the
-- "where ... denotes ..." between two equations) becomes a paragraph.
local function equation_rows(tbl)
  local out = {}
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      local cells, number, has_math, wide = {}, nil, false, nil
      for _, cell in ipairs(row.cells) do
        local parts = cell_parts(cell.contents)
        local tex, plain = {}, {}
        for _, p in ipairs(parts) do
          if p.math then
            has_math = true
            table.insert(tex, p.math)
          else
            -- Not %s, which takes the second byte of a no-break space alone.
            local s = p.text:gsub("\u{a0}", " "):gsub("[ \t\r\n]+", " ")
            if s:match("%S") then
              table.insert(plain, s)
              table.insert(tex, "\\text{" .. tex_text(s) .. "}")
            end
          end
        end
        local tag = #parts == 1 and parts[1].text
          and parts[1].text:match("^%s*%(([%w.%-]+)%)%s*$")
        if tag then
          number = tag
        elseif #tex > 0 then
          table.insert(cells, table.concat(tex, " "))
          -- A cell across the columns is prose (\intertext) when it has words
          -- of its own; one that is all mathematics is a split equation.
          if cell.col_span > 1 and #plain > 0 then wide = cell end
        end
      end
      if wide and #cells == 1 or not has_math and #cells > 0 then
        -- Prose: keep the cells' own inlines, inline math included.
        for _, cell in ipairs(row.cells) do
          for _, b in ipairs(cell.contents) do
            table.insert(out, b.t == "Plain" and pandoc.Para(b.content) or b)
          end
        end
      elseif #cells > 0 then
        local tex = cells[1]
        for k = 2, #cells do
          tex = tex .. (continues(cells[k]) and "" or " \\qquad ") .. cells[k]
        end
        if number then tex = tex .. " \\tag{" .. number .. "}" end
        table.insert(out, pandoc.Para({ pandoc.Math("DisplayMath", tex) }))
      end
    end
  end
  return out
end

-- A table nested in a cell is how LaTeX \makecell / \shortstack line breaks
-- come through ("Num. of" / "Samples"). Collapse a one-column nested table to
-- its cells' text joined by spaces.
local function flatten_cell_tables(blocks)
  return pandoc.walk_block(pandoc.Div(blocks), {
    Table = function(inner)
      local parts = {}
      for _, body in ipairs(inner.bodies) do
        for _, row in ipairs(body.body) do
          if #row.cells ~= 1 then return nil end
          local text = pandoc.utils.stringify(row.cells[1].contents)
          if text ~= "" then table.insert(parts, pandoc.Str(text)) end
          table.insert(parts, pandoc.Space())
        end
      end
      return pandoc.Plain(parts)
    end,
  }).content
end

-- In a pipe table a bare | inside math would end the cell.
local function escape_math_pipes(el)
  return pandoc.walk_block(pandoc.Div({ el }), {
    Math = function(m)
      m.text = m.text:gsub("\\|", "\\Vert "):gsub("|", "\\vert ")
      return m
    end,
  }).content[1]
end

local function clean_row(row, head)
  row.attr = pandoc.Attr()
  for _, cell in ipairs(row.cells) do
    cell.attr = pandoc.Attr()
    cell.contents = flatten_cell_tables(cell.contents)
    if head then
      -- Bold column titles say nothing the header row does not.
      cell.contents = pandoc.walk_block(pandoc.Div(cell.contents), {
        Strong = function(s) return s.content end,
      }).content
    end
  end
end

local function has_class(row, class)
  for _, cell in ipairs(row.cells) do
    if cell.classes:includes(class) then return true end
  end
  return false
end

-- LaTeXML marks a header row (<thead>, <th>) only sometimes; without one,
-- pandoc writes an empty header and the real header becomes the first data
-- row. The rule under the header is the cue: up to three leading rows ending
-- in a bottom rule, or followed by a row with a top rule (\midrule), become
-- the head. The head grows to take in the rows a header cell spans
-- ("Length" over "Memory" / "Ability"), as long as it stays within three.
-- A row of results LaTeXML took for a header: a label, then nothing but
-- decimal numbers and dashes.
local function is_data_row(row)
  local cells = row.cells
  if #cells < 3 or not pandoc.utils.stringify(cells[1].contents):match("%a") then return false end
  local numbers = 0
  for i = 2, #cells do
    local text = pandoc.utils.stringify(cells[i].contents):gsub("[%s\u{a0}*†‡%%]", "")
    if text:match("^[+-]?%d*%.%d+$") then
      numbers = numbers + 1
    elseif not (text == "" or text == "-" or text == "–" or text == "—") then
      return false
    end
  end
  return numbers >= 2
end

-- The head without the rows of results at its end; they open the body.
local function demote_data_rows(tbl)
  local rows = tbl.head.rows
  if #tbl.bodies == 0 then return end
  while #rows > 1 and is_data_row(rows[#rows]) do
    tbl.bodies[1].body:insert(1, rows:remove())
  end
  tbl.head.rows = rows
end

local function promote_header(tbl)
  if #tbl.bodies == 0 then return end
  local limit = 3
  if #tbl.head.rows > 0 then
    demote_data_rows(tbl)
    return
  end
  -- Leading rows of <th> cells in a <tbody> are the head: pandoc keeps them
  -- as the body's own head, which is written after any row promoted here.
  -- The rows under them, down to the rule, are promoted as below.
  local head = pandoc.List()
  if #tbl.bodies[1].head > 0 then
    head = tbl.bodies[1].head
    tbl.bodies[1].head = pandoc.List()
    limit = limit - #head
  end
  local rows = tbl.bodies[1].body
  local k
  for r = 1, math.min(limit, #rows - 1) do
    if has_class(rows[r], "ltx_border_b") or has_class(rows[r], "ltx_border_bb")
        or has_class(rows[r + 1], "ltx_border_t") then
      k = r
      break
    end
  end
  if k then
    local r = 1
    while r <= k do
      for _, cell in ipairs(rows[r].cells) do
        k = math.max(k, r + cell.row_span - 1)
      end
      r = r + 1
    end
    if k > limit or k >= #rows then k = nil end
  end
  -- Under rows already marked as the head, only a row that is itself
  -- ruled off from the body joins them, and not a row of results.
  if k and #head > 0 then
    for r = 1, k do
      if is_data_row(rows[r]) then k = nil break end
    end
  end
  local rest = pandoc.List()
  for r, row in ipairs(rows) do
    if k and r <= k then head:insert(row) else rest:insert(row) end
  end
  if #head == 0 then return end
  tbl.head.rows = head
  tbl.bodies[1].body = rest
  demote_data_rows(tbl)
end

function Table(tbl)
  if is_equation(tbl) then
    return equation_rows(tbl)
  end
  -- A table with nothing in it (title-page layout) would be an empty grid.
  -- An image or a code listing is content, though it has no text to stringify.
  local has_content = false
  local function found() has_content = true end
  pandoc.walk_block(pandoc.Div({ tbl }), { Image = found, CodeBlock = found })
  if not has_content and not pandoc.utils.stringify(tbl):match("%S") then
    return {}
  end
  promote_header(tbl)
  tbl.attr = pandoc.Attr()
  tbl.head.attr = pandoc.Attr()
  for i, spec in ipairs(tbl.colspecs) do
    tbl.colspecs[i] = { spec[1], pandoc.ColWidthDefault }
  end
  for _, row in ipairs(tbl.head.rows) do clean_row(row, true) end
  for _, body in ipairs(tbl.bodies) do
    body.attr = pandoc.Attr()
    for _, row in ipairs(body.head) do clean_row(row) end
    for _, row in ipairs(body.body) do clean_row(row) end
  end
  for _, row in ipairs(tbl.foot.rows) do clean_row(row) end
  return escape_math_pipes(tbl)
end

-- A footnote arrives inside the sentence it annotates: its mark, the mark
-- again, its number and its text, all inline ("a dataset11 1 Despite some
-- ..."). The mark stays where it is, once, and the text follows the block
-- (paragraph, list, table or figure) it belongs to, behind the same mark.
local function is_note_label(el)
  return el.t == "Span" and (el.classes:includes("ltx_tag_note") or el.classes:includes("ltx_note_type"))
end

local function note_parts(span)
  local mark, text = nil, pandoc.List()
  for _, el in ipairs(span.content) do
    if el.t == "Superscript" and not mark then
      mark = el
    elseif el.t == "Span" and el.classes:includes("ltx_note_outer") then
      local inner = el.content
      if #inner == 1 and inner[1].t == "Span" and inner[1].classes:includes("ltx_note_content") then
        inner = inner[1].content
      end
      local marked = false
      for _, part in ipairs(inner) do
        if part.t == "Superscript" and not marked then
          marked = true
          mark = mark or part
        elseif not is_note_label(part) then
          text:insert(part)
        end
      end
    end
  end
  while #text > 0 and (text[1].t == "Space" or text[1].t == "SoftBreak") do text:remove(1) end
  return mark, text
end

local function lift_notes(blocks)
  local out = pandoc.List()
  for _, block in ipairs(blocks) do
    if block.t == "Div" then
      block.content = lift_notes(block.content)
      out:insert(block)
    else
      local notes = pandoc.List()
      block = pandoc.walk_block(block, {
        Span = function(span)
          if not span.classes:includes("ltx_note") then return nil end
          local mark, text = note_parts(span)
          if pandoc.utils.stringify(text):match("%S") then
            local note = pandoc.List()
            if mark then note:extend({ mark, pandoc.Space() }) end
            note:extend(text)
            notes:insert(pandoc.Para(note))
          end
          return mark and { mark } or {}
        end,
      })
      -- Notes with no place in the text (\\footnotetext under the abstract)
      -- leave a paragraph of marks alone ("†††"); the notes say it all.
      local only_marks = #notes > 0 and (block.t == "Para" or block.t == "Plain")
      for _, el in ipairs(only_marks and block.content or {}) do
        if el.t ~= "Superscript" and not is_space(el) then only_marks = false end
      end
      if not only_marks then out:insert(block) end
      out:extend(notes)
    end
  end
  return out
end

-- Where pandoc writes a block as HTML (a table with merged cells), it renders
-- the mathematics itself: a number in a <span>, anything it cannot draw as
-- loose TeX with the "\pm" gone. Every formula leaves as its TeX between two
-- marks instead, and html-to-markdown.py writes it for where it landed (see
-- write_math there).
local MATH_MARKS = {
  InlineMath = { "\u{E000}", "\u{E001}" }, DisplayMath = { "\u{E002}", "\u{E003}" },
}

local function mark_math(m)
  local marks = MATH_MARKS[m.mathtype]
  return pandoc.RawInline("html", marks[1] .. m.text .. marks[2])
end

return {
  { Pandoc = function(doc)
      doc.blocks = lift_notes(doc.blocks)
      return doc
    end },
  { Div = Div, Math = Math, Inlines = Inlines, Header = Header, Span = Span, Para = Para, Plain = Plain,
    Link = Link, Image = Image, Figure = Figure, Table = Table },
  { Math = mark_math },
}
