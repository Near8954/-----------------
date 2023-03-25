def format_dms_coordinates(coordinates):
    return f"{coordinates[0]}° {coordinates[1]}\' {coordinates[2]}\""


def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
    decimal_degrees = coordinates[0] + \
        coordinates[1] / 60 + \
        coordinates[2] / 3600

    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees

    return decimal_degrees


def draw_map_for_location(latitude, latitude_ref, longitude, longitude_ref):
    import webbrowser

    decimal_latitude = dms_coordinates_to_dd_coordinates(
        latitude, latitude_ref)
    decimal_longitude = dms_coordinates_to_dd_coordinates(
        longitude, longitude_ref)
    url = f"https://www.google.com/maps?q={decimal_latitude},{decimal_longitude}"
    webbrowser.open_new_tab(url)
