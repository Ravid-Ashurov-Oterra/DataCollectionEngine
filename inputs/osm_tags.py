buildings_tags = {
    "building": True,  # catches all building types (residential, commercial, etc.)
    "man_made": ["works", "building", "storage_tank", "tower", "wastewater_plant", "chimney"],
    "amenity": ["industrial", "college", "school", "hospital"],  # often have large buildings
    "office": True,  # office buildings
    "shop": True,    # retail buildings
    "craft": True,   # workshops or small production
    "power": ["plant", "substation"]  # utility infrastructure
}

vegetation_tags = {
    "landuse": ["forest", "orchard", "vineyard"],
    "natural": ["wood", "scrub", "vegetation"],
    "landcover": ["trees"]
}

parks_tags = {
    "landuse": [ "meadow", "grass", "farmland"],
    "natural": ["grassland"],
    "leisure": ["park"],
    "landcover": ["grass"]
}

roads_tags = {
    "highway": ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential",
                "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link",
                "service", "living_street", "road", "track"]
}

schools_tags = {
    "amenity": [
        "school", "kindergarten", "college", "university", "library",
    ]}

religion_tags = {
    "amenity": [
        "place_of_worship",
    ]
}

amenities_tags = {
    "amenity": [
        # Healthcare
        "hospital", "clinic", "doctors", "dentist", "pharmacy",

        # Public Services
        "police", "fire_station", "post_office", "townhall", "community_centre", "courthouse",

        # Sanitary & Utilities
        "toilets", "drinking_water", "waste_disposal", "recycling", "water_point",

        # Transportation
        "bus_station", "ferry_terminal", "taxi", "bicycle_parking", "car_rental",

        # Leisure & Culture
        "cinema", "theatre", "arts_centre", "museum",

        # Food & Drink
        "restaurant", "cafe", "bar", "fast_food", "pub",

        # Accommodation
        "hotel", "guest_house", "hostel", "motel", "shelter",

        # Sports & Recreation
        "swimming_pool", "gym", "sports_centre", "stadium"
    ]
}

water_tags = {
    'natural': ['water', 'wetland', 'bay', 'strait', 'coastline'],
    'waterway': True,        
    'water': True ,          
    'landuse': ['reservoir'],
}

food_tags = {
    "amenity": [
        "restaurant",
        "fast_food",
        "cafe",
        "bar",
        "pub",
        "food_court",
        "biergarten"
    ],
    "shop": [
        "supermarket",
        "convenience",
        "greengrocer",
        "butcher",
        "bakery",
        "deli",
        "cheese",
        "chocolate",
        "seafood",
        "beverages",
        "alcohol",
        "wine",
        "coffee",
        "tea"
    ],
    "craft": [
        "bakery",
        "butcher",
        "cheese",
        "confectionery"
    ],
    "vending": [
        "food",
        "drinks",
        "milk",
        "bread"
    ],
    "marketplace": True
}

built_heights_tags = {
      "building": True,
      "man_made": ["works", "building", "storage_tank", "tower", "wastewater_plant", "chimney"],
      "amenity": ["industrial", "college", "school", "hospital", "kindergarten", "university", "library", "place_of_worship", "clinic"],
      "office": True,
      "shop": True,
      "craft": True,
      "power": ["plant", "substation"]
  }