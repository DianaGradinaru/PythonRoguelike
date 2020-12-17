import constants


def select(board, wanted):
    return [item for item in board if item.get("type") == wanted]


def distance(points):
    return (points[1][0] - points[0][0], points[1][1] - points[0][1])


def message(text, color=constants.COLOR_PLAYER):
    return {"text": text, "color": color}


def start_msg():
    return [
        message("Have you got what it takes"),
        message("to pass your PA?"),
        message(""),
    ]


def end_msg():
    return [
        message(""),
        message("Good luck!"),
        message(""),
    ]
