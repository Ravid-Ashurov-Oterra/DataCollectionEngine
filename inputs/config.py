LANE_WIDTH_M = 3.0  # 3 meters (assumed)

# RES 12 config
H3_RES = 12
SOFTENING_STRENGTH = 1

# # RES 15 config
# H3_RES = 15
# SOFTENING_STRENGTH = 6

NO_SOFTEN_TILE_FUNCTIONS = [ "road", "built", "school", "religious", "amenity", "food"]
DEFAULT_LEVEL_HEIGHT_M = 3.0  # Default height per building level if height is not explicitly provided
DEFAULT_BUILDING_HEIGHT_M = 12.1  # Default height for buildings without explicit height
# OFFSET_LEFT = (1/111.320)*0.05
# OFFSET_TOP = (1/110.574)*0.05
OFFSET_LEFT = (1/111.320)*0.075
OFFSET_TOP = (1/110.574)*0.075

CENTER = {
    'lat': 32.224768,
    'lng': 35.302738
}

# tiff based BBox
BOUNDING_BOX = {
    'north': 32.231184487551396,
    'south': 32.21163604303779,
    'west': 35.273042715328806,
    'east': 35.305007307487806
}

# # Origin BBox  
# BOUNDING_BOX = {
#     'north': 32.2311823,
#     'south': 32.2116428,
#     'west': 35.2730451,
#     'east': 35.3050055``
# }

ZOOM_TOP_LEFT = {
    # open area with slopes
    'east': BOUNDING_BOX['east'] - OFFSET_LEFT* 21.5, 
    'north': BOUNDING_BOX['north'] - OFFSET_TOP
}

# ZOOM_TOP_LEFT = {
#     'north': 32.229282,
#     'east': 35.294851
# }

# ZOOM_TOP_LEFT = {
#     # road roundabout
#     'north': CENTER['lat'] - OFFSET_TOP, 
#     'east': CENTER['lng'] - OFFSET_LEFT
# }

# ZOOM_TOP_LEFT = {
#     "north": 32.227535483268014,
#     "east": 35.289040987468695
# }
# ZOOM_TOP_LEFT = {
#     "north": 32.230644,
#     "east": 35.285250
#     # 32.230644, 35.285250
# }


# ZOOM_TOP_LEFT = {
#     # open area with slopes
#     'north': BOUNDING_BOX['north'] - OFFSET_TOP,
#     "east": BOUNDING_BOX['east'] - OFFSET_LEFT* 2.5
# }

# ZOOM_TOP_LEFT = {
#     # built area
#     'north': BOUNDING_BOX['north'] - OFFSET_TOP * 3,
#     'east': BOUNDING_BOX['east'] - OFFSET_LEFT
# }

# ZOOM_IN_BBOX = {
#     'north': ZOOM_TOP_LEFT['north'] - OFFSET_TOP, 
#     'south': ZOOM_TOP_LEFT['north'] + OFFSET_TOP, 
#     'east': ZOOM_TOP_LEFT['east'] - OFFSET_LEFT, 
#     'west': ZOOM_TOP_LEFT['east'] + OFFSET_LEFT
# }
ZOOM_IN_BBOX = BOUNDING_BOX

# ZOOM_IN_BBOX = {
#     "north": 32.23118431773797,
#     "south": 32.23028027737828,
#     "east": 35.28569342138099,
#     "west": 35.28479551136178
# }
