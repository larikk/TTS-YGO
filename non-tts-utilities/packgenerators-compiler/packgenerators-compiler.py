import os
import string
import re

sections = [
    "core-sets",
    "battle-packs",
    "tournament-packs",
]

logic_dir = "../../src/pack-spawning/pack-logic/"
output_path = "../../src/gui/PackGenerators.ttslua"

taken_codes = {} # set for checking if each code is unique
processed_files = []
skipped_files = []

section_mapping = dict() # maps core-sets to Core Sets

for section in sections:
    human_readable = string.capwords(section.replace("-", " "))
    section_mapping[section] = f"'{human_readable}'"


prefix = f"""-- autogenerated with packgenerators-compiler, do not modify manually
local packGenerators = {{}} -- all generators for quick access via the setcode
local sections = {{}} -- partitioned over the sections and ordered by release for building the gui
local sectionOrder = {'{' + ", ".join([section_mapping[s] for s in sections]) + '}'}

for _,v in ipairs(sectionOrder) do
    sections[v] = {{}}
end

local gen = nil
"""

suffix = """
return {
    packGenerators = packGenerators,
    sectionOrder = sectionOrder,
    sections = sections
}
"""

def createEntry(pack, section):
    without_extension = pack.split(".")[0]
    code = without_extension.split("-")[1]
    return f"""
gen = require("TTS-YGO-sealed-draft/src/pack-spawning/pack-logic/{section}/{without_extension}"):new()
packGenerators['{code}'] = gen
gen.assetCode = '{code}'
table.insert(sections[{section_mapping[section]}], gen)
"""

output = prefix

for section in sections:
    path = logic_dir + section
    output += f"\n-- {section}"
    for pack in os.listdir(path):
        if re.match(r"^[0-9]{3}-.+\.ttslua$", pack):
            output += createEntry(pack, section)
            processed_files.append(section + "/" + pack)
        else:
            skipped_files.append(section + "/" + pack)
    output += "--##################\n\n"

output += suffix

with open(output_path, "w") as f:
    f.write(output)