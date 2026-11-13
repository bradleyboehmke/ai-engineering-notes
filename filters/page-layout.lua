-- Shared page layout for every content page, driven by front matter
-- (ADR-0001 schema). Pages without a `type` (Start Here, views) are untouched.
--
-- Prepends a `<div class="page-meta">` block to the body, right under the
-- title. Its parts, each with a stable class for later checks and styling:
--   .page-theme      theme display name (from data/themes.yml), plus stage
--   .page-maturity   seed / draft / solid
--   .page-lens-leader  present only on leader pages (lens: leader)
--   .page-prereqs    one <a class="prereq" data-prereq="<slug>"> per prereq
-- and, when `video` is set, a `<div class="page-video">` embed after it.

local CONTENT_FOLDERS = { "topics", "dictionary", "essays", "prototypes", "tools" }

local function project_dir()
  return (quarto.project and quarto.project.directory) or "."
end

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return text
end

-- data/themes.yml is a YAML list; parse it with pandoc by wrapping it as
-- front matter under a `themes` key. Returns { [slug] = {title=, stage=} }.
local function load_themes()
  local text = read_file(project_dir() .. "/data/themes.yml")
  if not text then error("page-layout: cannot read data/themes.yml") end
  local indented = text:gsub("([^\n]*)", "  %1")
  local doc = pandoc.read("---\nthemes:\n" .. indented .. "\n---\n", "markdown")
  local themes = {}
  for _, t in ipairs(doc.meta.themes) do
    themes[pandoc.utils.stringify(t.slug)] = {
      title = pandoc.utils.stringify(t.title),
      stage = t.stage and pandoc.utils.stringify(t.stage) or "",
    }
  end
  return themes
end

local function str(meta, key)
  local v = meta[key]
  if v == nil then return "" end
  return pandoc.utils.stringify(v)
end

local function list(meta, key)
  local v = meta[key]
  local out = {}
  if v == nil then return out end
  if pandoc.utils.type(v) ~= "List" then v = { v } end
  for _, item in ipairs(v) do
    local s = pandoc.utils.stringify(item)
    if s ~= "" then table.insert(out, s) end
  end
  return out
end

-- Find the page whose file stem is `slug` in any content folder. Returns its
-- project-absolute .qmd/.md path (Quarto rewrites it to a relative .html link)
-- and its title, or nil when no such page exists.
local function find_page(slug)
  for _, folder in ipairs(CONTENT_FOLDERS) do
    for _, ext in ipairs({ ".qmd", ".md" }) do
      local rel = folder .. "/" .. slug .. ext
      local text = read_file(project_dir() .. "/" .. rel)
      if text then
        local doc = pandoc.read(text, "markdown")
        local title = str(doc.meta, "title")
        return "/" .. rel, (title ~= "" and title or slug)
      end
    end
  end
  return nil
end

local function prereq_link(slug)
  local href, title = find_page(slug)
  if not href then
    -- Left dangling on purpose so the prereq link checker reports it.
    href, title = slug .. ".html", slug
  end
  return pandoc.Link(title, href, "", { class = "prereq", ["data-prereq"] = slug })
end

-- YouTube watch / short URLs become embed URLs; anything else is used as is.
local function embed_url(url)
  local id = url:match("youtube%.com/watch%?.*v=([%w_-]+)")
    or url:match("youtu%.be/([%w_-]+)")
    or url:match("youtube%.com/embed/([%w_-]+)")
  if id then return "https://www.youtube.com/embed/" .. id end
  return url
end

local function span(class, inlines, attrs)
  attrs = attrs or {}
  attrs.class = class
  return pandoc.Span(inlines, attrs)
end

function Pandoc(doc)
  local meta = doc.meta
  if str(meta, "type") == "" then return nil end

  local themes = load_themes()
  local slug = str(meta, "theme")
  local theme = themes[slug] or { title = slug, stage = "" }
  local label = "Theme: " .. theme.title
  if theme.stage ~= "" then label = label .. " (Stage " .. theme.stage .. ")" end

  local maturity = str(meta, "maturity")
  local parts = {
    span("page-theme", { pandoc.Str(label) }, { ["data-theme"] = slug }),
    span("page-maturity", { pandoc.Str("Maturity: " .. maturity) },
      { ["data-maturity"] = maturity }),
  }

  if str(meta, "lens") == "leader" then
    table.insert(parts, span("page-lens-leader", { pandoc.Str("Leader page") }))
  end

  local prereqs = list(meta, "prereqs")
  if #prereqs > 0 then
    local inlines = { pandoc.Str("Before this: ") }
    for i, p in ipairs(prereqs) do
      if i > 1 then table.insert(inlines, pandoc.Str(", ")) end
      table.insert(inlines, prereq_link(p))
    end
    table.insert(parts, span("page-prereqs", inlines))
  end

  local line = {}
  for i, part in ipairs(parts) do
    if i > 1 then table.insert(line, pandoc.Str(" · ")) end
    table.insert(line, part)
  end
  local blocks = { pandoc.Div({ pandoc.Plain(line) }, { class = "page-meta" }) }

  local video = str(meta, "video")
  if video ~= "" then
    table.insert(blocks, pandoc.RawBlock("html", string.format(
      '<div class="page-video ratio ratio-16x9"><iframe src="%s" title="Video" '
        .. 'allowfullscreen loading="lazy"></iframe></div>', embed_url(video))))
  end

  for i = #blocks, 1, -1 do table.insert(doc.blocks, 1, blocks[i]) end
  return doc
end
