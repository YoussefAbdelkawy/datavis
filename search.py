from charts.shared import WORK_TYPES, YEARS

# word or two-word phrase -> (filter, value)
KEYWORDS = {
    "manhattan": ("borough", "MANHATTAN"),
    "brooklyn": ("borough", "BROOKLYN"), "bk": ("borough", "BROOKLYN"),
    "queens": ("borough", "QUEENS"),
    "bronx": ("borough", "BRONX"),
    "staten island": ("borough", "STATEN ISLAND"), "si": ("borough", "STATEN ISLAND"),
    "pedestrian": ("person", "Pedestrian"), "pedestrians": ("person", "Pedestrian"),
    "walker": ("person", "Pedestrian"), "walkers": ("person", "Pedestrian"), "ped": ("person", "Pedestrian"),
    "cyclist": ("person", "Cyclist"), "cyclists": ("person", "Cyclist"), "bike": ("person", "Cyclist"),
    "bikes": ("person", "Cyclist"), "biker": ("person", "Cyclist"), "bikers": ("person", "Cyclist"),
    "bicycle": ("person", "Cyclist"),
    "motorist": ("person", "Motorist"), "motorists": ("person", "Motorist"), "driver": ("person", "Motorist"),
    "drivers": ("person", "Motorist"), "car": ("person", "Motorist"), "cars": ("person", "Motorist"),
}
KEYWORDS.update({year: ("year", year) for year in YEARS})
# full work type labels, e.g. "sidewalk shed"
KEYWORDS.update({label.lower(): ("work", label) for label in WORK_TYPES})

# short words for the work type labels
SHORT_WORDS = {
    "Sidewalk Shed": ["shed", "sheds"],
    "Supported Scaffold": ["scaffold", "scaffolds", "scaffolding", "supported"],
    "Suspended Scaffold": ["suspended"],
    "Construction Fence": ["fence", "fences", "fencing"],
    "Full Demolition": ["demolition", "demo"],
    "Earth Work": ["earth", "excavation"],
    "Foundation": ["foundation", "foundations"],
    "General Construction": ["construction", "general"],
}
for label, words in SHORT_WORDS.items():
    KEYWORDS.update({word: ("work", label) for word in words})


def parse_search(text):
    # read words left to right; two-word phrases win over single words
    words = text.lower().replace(",", " ").split()
    found, ignored = {}, []
    i = 0
    while i < len(words):
        pair = " ".join(words[i:i + 2])
        if pair in KEYWORDS:
            name, value = KEYWORDS[pair]
            i += 2
        elif words[i] in KEYWORDS:
            name, value = KEYWORDS[words[i]]
            i += 1
        else:
            ignored.append(words[i])
            i += 1
            continue
        found[name] = value
    found["ignored"] = ignored
    return found
