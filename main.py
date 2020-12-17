import tcod
from os.path import join
from time import sleep

import constants
import engine
import util


def setup():
    tileset = tcod.tileset.load_tilesheet(
        path=join("assets", "download.png"),
        columns=16,
        rows=16,
        charmap=tcod.tileset.CHARMAP_CP437,
    )
    context = tcod.context.new_terminal(
        columns=constants.SCREEN_WIDTH,
        rows=constants.SCREEN_HEIGHT,
        tileset=tileset,
        vsync=True,
        title="Pass the PA",
    )
    console = tcod.Console(
        width=constants.SCREEN_WIDTH,
        height=constants.SCREEN_HEIGHT,
        order="F",
    )
    return context, console


def main():
    context, console = setup()

    board = engine.create_board(filename=join("assets", "map.txt"))
    walls = util.select(board=board, wanted="wall")
    player = util.select(board=board, wanted="player").pop()
    items = util.select(board=board, wanted="item")
    enemy = util.select(board=board, wanted="enemy").pop()
    messages = util.start_msg()

    game_running = True
    while game_running:

        if player.get("kp") == 0:
            messages = [
                util.message("Oh no! The PA has proven", constants.COLOR_ENEMY),
                util.message("too much for you", constants.COLOR_ENEMY),
                util.message("You should keep studying", constants.COLOR_ENEMY),
            ]
            sleep(10)
            game_running = False

        if enemy.get("kp") == 0:
            messages = [
                util.message("You have successfully", constants.COLOR_ITEM),
                util.message("passed your PA!", constants.COLOR_ITEM),
                util.message("Congratulations!", constants.COLOR_ITEM),
            ]
            sleep(5)
            game_running = False

        for event in tcod.event.wait():
            # window closed
            if event.type == "QUIT":
                messages += util.end_msg()

                game_running = False

            # key pressed
            if event.type == "KEYDOWN":

                general = {
                    "actor": player,
                    "board": board,
                    "walls": walls,
                    "items": items,
                    "opponent": enemy,
                    "messages": messages,
                }

                # only update enemy pathfinding on keypress
                enemy["path"] = engine.path_between(
                    actor=enemy,
                    target=player,
                    walls=walls,
                )

                # quit
                if event.sym == tcod.event.K_ESCAPE:
                    messages += util.end_msg()

                    game_running = False

                # wait
                if event.sym == tcod.event.K_SPACE:
                    if len(enemy.get("path")) <= constants.ENEMY_SIGHT:
                        enemy_general = dict(**general)
                        enemy_general["actor"] = enemy
                        enemy_general["opponent"] = player

                        engine.enemy_turn(**enemy_general)

                # move
                if event.sym in [
                    tcod.event.K_w,
                    tcod.event.K_UP,
                    tcod.event.K_s,
                    tcod.event.K_DOWN,
                    tcod.event.K_a,
                    tcod.event.K_LEFT,
                    tcod.event.K_d,
                    tcod.event.K_RIGHT,
                ]:

                    if event.sym in [tcod.event.K_w, tcod.event.K_UP]:
                        direction = {"dx": 0, "dy": -1}

                    if event.sym in [tcod.event.K_s, tcod.event.K_DOWN]:
                        direction = {"dx": 0, "dy": 1}

                    if event.sym in [tcod.event.K_a, tcod.event.K_LEFT]:
                        direction = {"dx": -1, "dy": 0}

                    if event.sym in [tcod.event.K_d, tcod.event.K_RIGHT]:
                        direction = {"dx": 1, "dy": 0}

                    engine.movement(**general, **direction)

                # got too close to the PA
                if len(enemy.get("path")) <= constants.ENEMY_SIGHT:
                    enemy_general = dict(**general)
                    enemy_general["actor"] = enemy
                    enemy_general["opponent"] = player

                    engine.enemy_turn(**enemy_general)

        # render
        engine.render(
            board=board,
            player=player,
            messages=messages,
            context=context,
            console=console,
        )

    # quit
    sleep(1)
    raise SystemExit()


if __name__ == "__main__":
    main()
