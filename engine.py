from numpy import ones, int8
from tcod.path import SimpleGraph, Pathfinder
from random import random, randint
from time import sleep

import constants
import util


def create_board(filename):
    board = []
    with open(filename) as file:
        for y, row in enumerate(file):
            for x, cell in enumerate(row):
                if cell == "#":
                    board.append(create_wall(x=x, y=y))

                if cell == "@":
                    board.append(create_player(x=x, y=y))

                if cell == "*":
                    board.append(create_item(x=x, y=y))

                if cell == "+":
                    board.append(create_enemy(x=x, y=y))

    return board


def create_wall(x, y):
    return {
        "x": x,
        "y": y,
        "icon": "#",
        "color": constants.COLOR_WALL,
        "type": "wall",
        "name": "a wall",
        "blocker": True,
    }


def create_player(x, y):
    return {
        "x": x,
        "y": y,
        "icon": "@",
        "color": constants.COLOR_PLAYER,
        "type": "player",
        "name": "the Codecooler",
        "kp": 25,
    }


def create_item(x, y):
    base = {
        "x": x,
        "y": y,
        "color": constants.COLOR_ITEM,
        "type": "item",
    }
    types = [
        {"icon": "$", "name": "a Codewars Kata", "kp": 10},
        {"icon": "%", "name": "a Programming Language", "kp": 25},
    ]

    if random() > 0.75:
        return dict(**base, **types[1])

    return dict(**base, **types[0])


def create_enemy(x, y):
    return {
        "x": x,
        "y": y,
        "icon": ".",
        "color": constants.COLOR_ENEMY,
        "type": "enemy",
        "name": "The Dreaded PA",
        "blocker": True,
        "kp": 100,
        "path": [],
    }


def render(board, player, messages, context, console):
    console.clear()

    for piece in board:
        console.print(
            x=piece.get("x"),
            y=piece.get("y"),
            string=piece.get("icon"),
            fg=piece.get("color"),
        )

    console.print(
        x=1,
        y=constants.SCREEN_HEIGHT - 4,
        string=player.get("name"),
        fg=constants.COLOR_ITEM,
    )
    console.print(
        x=1,
        y=constants.SCREEN_HEIGHT - 3,
        string=f"knowledge points: {player.get('kp')}",
        fg=constants.COLOR_PLAYER,
    )

    for m, message in enumerate(messages[-3:]):
        x = constants.SCREEN_WIDTH - len(message.get("text")) - 1
        y = constants.SCREEN_HEIGHT - 4 + m

        console.print(
            x=x,
            y=y,
            string=message.get("text"),
            fg=message.get("color"),
        )

    context.present(console)


def attack(actor, opponent, messages):
    damage = randint(
        int(actor.get("kp") * 0.3),
        int(actor.get("kp") * 0.7),
    )
    opponent["kp"] = max(0, opponent.get("kp") - damage)

    if opponent.get("kp") == 0:
        messages.append(
            util.message(f"{actor.get('name')} has defeated {opponent.get('name')}!")
        )


def movement(actor, board, walls, items, opponent, messages, dx, dy):
    dest_x = actor.get("x") + dx
    dest_y = actor.get("y") + dy

    # what's there?
    thing = [
        item for item in board if item.get("x") == dest_x and item.get("y") == dest_y
    ]

    # nothing
    if len(thing) == 0:
        actor["x"] = dest_x
        actor["y"] = dest_y

    else:
        msg_color = constants.COLOR_PLAYER
        thing = thing.pop()

        # a wall
        if thing in walls:
            action = "bumps into"

        # an item
        if thing in items:

            if actor.get("type") == "player":
                actor["kp"] += thing.get("kp")

                if thing.get("mk") is not None:
                    actor["mk"] += thing.get("mk")

                items.remove(thing)
                board.remove(thing)
                # have to remove it from both

            actor["x"] = dest_x
            actor["y"] = dest_y

            msg_color = constants.COLOR_ITEM
            action = "masters"

        # the enemy
        if thing is opponent:
            msg_color = constants.COLOR_ENEMY
            action = "attacks"

            attack(actor=actor, opponent=opponent, messages=messages)

        # print
        messages.append(
            util.message(
                text=f"{actor.get('name')} {action} {thing.get('name')}",
                color=msg_color,
            )
        )


def path_between(actor, target, walls):

    level_width = sorted(walls, key=lambda obj: obj.get("x"))
    level_width = level_width[-1].get("x") - level_width[0].get("x") + 1

    level_height = sorted(walls, key=lambda obj: obj.get("y"))
    level_height = level_height[-1].get("y") - level_height[0].get("y") + 1

    # https://python-tcod.readthedocs.io/en/latest/tcod/path.html#tcod.path.SimpleGraph

    cost = ones((level_width, level_height), dtype=int8, order="F")

    for wall in walls:
        cost[wall.get("x"), wall.get("y")] = 0

    graph = SimpleGraph(cost=cost, cardinal=2, diagonal=3)
    pathfinder = Pathfinder(graph=graph)

    pathfinder.add_root((actor.get("x"), actor.get("y")))
    return pathfinder.path_to((target.get("x"), target.get("y"))).tolist()


def enemy_turn(actor, board, walls, items, opponent, messages):
    path = util.distance(actor.get("path"))

    movement(
        actor=actor,
        board=board,
        walls=walls,
        items=items,
        opponent=opponent,
        messages=messages,
        dx=path[0],
        dy=path[1],
    )
