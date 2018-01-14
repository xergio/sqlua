localesMap = {
'enUS': 0,
'koKR': 1,
'frFR': 2,
'deDE': 3,
'zhCN': 4,
'twCN': 5, # ?
'esES': 6,
'esSA': 7, # ?
'ruRU': 8,
}

def escapeDoubleQuotes(inp):
    name = inp.replace('"', '\\"')
    return name

def escapeQuotes(inp):
    name = inp.replace("'", "\\'")
    return name
