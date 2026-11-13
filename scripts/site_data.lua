-- Read the site's data files (data/themes.yml, data/types.yml) for the Lua
-- side of the build: scripts/views.lua (pre-render) and
-- filters/page-layout.lua. The Python side reads the same files through
-- scripts/themes.py and scripts/page_types.py; both represent "no stage" as
-- nil / None, never "".
--
-- Load with `dofile(<project dir> .. "/scripts/site_data.lua")(<project dir>)`.

return function(root)
  local M = {}

  local function read_file(path)
    local f = assert(io.open(path, "r"), "site_data: cannot read " .. path)
    local text = f:read("a")
    f:close()
    return text
  end

  -- A data file is a YAML list of flat mappings. Parse it with pandoc by
  -- wrapping it as front matter under one key; values come back as strings,
  -- and empty values (`stage:`) as nil.
  local function load_list(rel)
    local indented = read_file(root .. "/" .. rel):gsub("([^\n]*)", "  %1")
    local doc = pandoc.read("---\nitems:\n" .. indented .. "\n---\n", "markdown")
    local items = {}
    for _, entry in ipairs(doc.meta.items) do
      local item = {}
      for key, value in pairs(entry) do
        local s = pandoc.utils.stringify(value)
        if s ~= "" then item[key] = s end
      end
      table.insert(items, item)
    end
    return items
  end

  -- Themes in file order: { slug, title, stage } with stage a number or nil.
  function M.themes()
    local themes = {}
    for _, t in ipairs(load_list("data/themes.yml")) do
      table.insert(themes, { slug = t.slug, title = t.title, stage = tonumber(t.stage) })
    end
    return themes
  end

  -- Themes in path order: by stage, then stageless themes; file order breaks
  -- ties. scripts/themes.py `path_order` orders them the same way.
  function M.path_order(themes)
    local ordered = {}
    for i, t in ipairs(themes) do ordered[i] = { theme = t, index = i } end
    table.sort(ordered, function(a, b)
      local sa, sb = a.theme.stage or math.huge, b.theme.stage or math.huge
      if sa ~= sb then return sa < sb end
      return a.index < b.index
    end)
    local out = {}
    for i, entry in ipairs(ordered) do out[i] = entry.theme end
    return out
  end

  -- Page types in file order: { type, folder, title, sort }.
  function M.types()
    return load_list("data/types.yml")
  end

  function M.content_folders()
    local folders = {}
    for _, t in ipairs(M.types()) do table.insert(folders, t.folder) end
    return folders
  end

  -- "Stage N" for a staged theme, nil for a theme without a stage.
  function M.stage_label(theme)
    if theme.stage then return "Stage " .. theme.stage end
    return nil
  end

  return M
end
