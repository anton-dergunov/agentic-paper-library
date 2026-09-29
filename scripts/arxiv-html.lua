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

-- Every control sequence KaTeX supports, generated from KaTeX itself.
local SUPPORTED = {}
do
  local dir = (PANDOC_SCRIPT_FILE or ""):match("(.*/)") or "./"
  for line in io.lines(dir .. "katex-commands.txt") do
    if not line:match("^#") then SUPPORTED[line] = true end
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
  -- Cross-references and citations: keep the label or key as text.
  ref = "\\text", eqref = "\\text", cref = "\\text", Cref = "\\text",
  autoref = "\\text", cite = "\\text", citep = "\\text", citet = "\\text",
}

-- Commands whose braced argument is text, not math.
local TEXT_CMDS = {
  text = true, textrm = true, textit = true, textbf = true, textsf = true,
  texttt = true, textup = true, textnormal = true, textsc = true, mbox = true,
  hbox = true, emph = true,
}

-- LaTeX layout commands that mean nothing in a rendered equation.
local LAYOUT = { "vskip", "hskip", "penalty", "hfil", "hfill", "indent", "noindent", "nobreak", "allowbreak" }

-- One pass over the TeX that knows, at each point, whether it is in math or in
-- the text argument of \text{...}, and fixes two things that depend on it:
--
-- * A "$" inside the TeX would end the markdown math span early. Inside text
--   ("\text{bo$n$}") it switches to math, so write it as \( ... \); in math
--   ("0.769$\pm$0.162") it is redundant, so drop it.
-- * A command KaTeX lacks: use its equivalent if there is one; otherwise it is
--   the paper's own macro (\rank, \defeq), shown as its name upright —
--   \operatorname in math, \textrm in text, where \operatorname is not allowed.
local function rewrite_commands(t)
  local out = {}
  local modes = { "math" }        -- mode of each open brace group
  local pending_text = false      -- the next "{" opens a text argument
  local dollar_open = false       -- inside a $...$ that began in text mode
  local i, n = 1, #t
  local function mode()
    if dollar_open then return "math" end
    return modes[#modes]
  end
  while i <= n do
    local c = t:sub(i, i)
    if c == "\\" then
      local name = t:match("^%a+", i + 1)
      if name then
        i = i + 1 + #name
        local cmd = "\\" .. name
        if not SUPPORTED[name] then
          if EQUIVALENT[name] then
            cmd = EQUIVALENT[name]
          elseif mode() == "text" then
            cmd = "\\textrm{" .. name .. "}"
          else
            cmd = "\\operatorname{" .. name .. "}"
          end
        end
        local base = cmd:match("^\\(%a+)$")
        pending_text = (base ~= nil and TEXT_CMDS[base]) or false
        table.insert(out, cmd)
      else
        -- "\\", "\{", "\$", "\ " and the like: copy both characters.
        table.insert(out, t:sub(i, i + 1))
        i = i + 2
      end
    elseif c == "{" then
      table.insert(modes, pending_text and "text" or mode())
      pending_text = false
      table.insert(out, c)
      i = i + 1
    elseif c == "}" then
      if #modes > 1 then table.remove(modes) end
      table.insert(out, c)
      i = i + 1
    elseif c == "$" then
      if modes[#modes] == "text" then
        table.insert(out, dollar_open and "\\)" or "\\(")
        dollar_open = not dollar_open
      end
      i = i + 1
    else
      if not c:match("%s") then pending_text = false end
      table.insert(out, c)
      i = i + 1
    end
  end
  return table.concat(out)
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
  for _, cmd in ipairs(LAYOUT) do
    t = t:gsub("\\" .. cmd .. "%s*%-?[%d.]*%a?%a?%f[^%a]", "")
  end
  return rewrite_commands(t)
end

function Math(m)
  m.text = normalise_math(m.text)
  return m
end

-- Two things that go wrong when math is written next to other text:
-- LaTeXML sometimes splits one expression into adjacent pieces, and "$a$$b$"
-- would open a display equation, so merge them; and a currency sign before
-- math ("\$" then "$15$") becomes "\$$15$", so move the sign into the math.
function Inlines(inlines)
  local out = pandoc.List()
  for _, el in ipairs(inlines) do
    local prev = out[#out]
    if el.t == "Math" and el.mathtype == "InlineMath" and prev then
      if prev.t == "Math" and prev.mathtype == "InlineMath" then
        prev.text = prev.text .. " " .. el.text
        goto continue
      end
      if prev.t == "Str" and prev.text:sub(-1) == "$" then
        prev.text = prev.text:sub(1, -2)
        if prev.text == "" then out:remove() end
        el.text = "\\$" .. el.text
      end
    end
    out:insert(el)
    ::continue::
  end
  return out
end

function Span(el)
  return el.content
end

-- With raw HTML on, any link or image carrying an id or class is written as an
-- HTML tag; without the attributes it stays a markdown link.
function Link(el)
  el.attr = pandoc.Attr()
  return el
end

function Image(el)
  el.attr = pandoc.Attr()
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

-- LaTeXML lays out numbered equations as tables whose cells hold the math and
-- the equation number. Turn each row into one display equation, with \tag{n}.
local function equation_rows(tbl)
  local out = {}
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      local maths, number = {}, nil
      for _, cell in ipairs(row.cells) do
        pandoc.walk_block(pandoc.Div(cell.contents), {
          Math = function(m) table.insert(maths, m.text) end,
          Str = function(s)
            local n = s.text:match("^%((%w+)%)$")
            if n then number = n end
          end,
        })
      end
      if #maths > 0 then
        local tex = table.concat(maths, " ")
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

local function clean_row(row)
  row.attr = pandoc.Attr()
  for _, cell in ipairs(row.cells) do
    cell.attr = pandoc.Attr()
    cell.contents = flatten_cell_tables(cell.contents)
  end
end

function Table(tbl)
  if is_equation(tbl) then
    return equation_rows(tbl)
  end
  tbl.attr = pandoc.Attr()
  for i, spec in ipairs(tbl.colspecs) do
    tbl.colspecs[i] = { spec[1], pandoc.ColWidthDefault }
  end
  for _, row in ipairs(tbl.head.rows) do clean_row(row) end
  for _, body in ipairs(tbl.bodies) do
    body.attr = pandoc.Attr()
    for _, row in ipairs(body.head) do clean_row(row) end
    for _, row in ipairs(body.body) do clean_row(row) end
  end
  for _, row in ipairs(tbl.foot.rows) do clean_row(row) end
  return escape_math_pipes(tbl)
end
