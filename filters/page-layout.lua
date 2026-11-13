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

local function project_dir()
  return (quarto.project and quarto.project.directory) or "."
end

-- Data files (themes, page types), shared with scripts/views.lua.
local data = dofile(project_dir() .. "/scripts/site_data.lua")(project_dir())

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local text = f:read("a")
  f:close()
  return text
end

-- { [slug] = theme } from data/themes.yml.
local function themes_by_slug()
  local themes = {}
  for _, t in ipairs(data.themes()) do themes[t.slug] = t end
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

-- Content pages by slug (file stem): { [slug] = { rel paths } }. Walks every
-- content folder, subfolders included, skipping folder `index` pages (views):
-- the same pages scripts/metadata.py validates prereqs against.
local slug_index
local function content_slugs()
  if slug_index then return slug_index end
  slug_index = {}
  local function walk(rel)
    local ok, names = pcall(pandoc.system.list_directory, project_dir() .. "/" .. rel)
    if not ok then return end
    table.sort(names)
    for _, name in ipairs(names) do
      local path = rel .. "/" .. name
      local stem = name:match("^(.+)%.q?md$")
      if stem and stem ~= "index" then
        slug_index[stem] = slug_index[stem] or {}
        table.insert(slug_index[stem], path)
      elseif not stem then
        walk(path)
      end
    end
  end
  for _, folder in ipairs(data.content_folders()) do walk(folder) end
  return slug_index
end

-- The one content page whose slug is `slug`: its project-absolute .qmd/.md
-- path (Quarto rewrites it to a relative .html link) and its title. nil when
-- no page, or more than one, has that slug (metadata validation names which).
local function find_page(slug)
  local paths = content_slugs()[slug]
  if not paths or #paths ~= 1 then return nil end
  local doc = pandoc.read(read_file(project_dir() .. "/" .. paths[1]), "markdown")
  local title = str(doc.meta, "title")
  return "/" .. paths[1], (title ~= "" and title or slug)
end

local function prereq_link(slug)
  local href, title = find_page(slug)
  if not href then
    -- Left dangling on purpose so the prereq link checker reports it. Quarto
    -- never publishes `_`-prefixed folders, so this can't resolve by accident
    -- (a bare `<slug>.html` could: `index.html`, or a same-folder namesake).
    href, title = "_prereq-not-found/" .. slug .. ".html", slug
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

  local slug = str(meta, "theme")
  local theme = themes_by_slug()[slug] or { title = slug } -- no stage
  local label = "Theme: " .. theme.title
  local stage = data.stage_label(theme)
  if stage then label = label .. " (" .. stage .. ")" end

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
