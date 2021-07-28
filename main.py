from collections import deque
from random import randint

from pynput.keyboard import Key, Listener

from consolet import Console, init_colorama
from consolet.utils import get_system_metrics

from colorama import Fore, Style

# Codes for Snake Position
RIGHT = 0
LEFT = 1
UP = 2
DOWN = 3

# Static Things
HASHTAG_ICON = '#'
SNAKE_ICON = '='
FOOD_ICON = '@'
world = list()
snake = deque([(5, i + 5) for i in range(4)])  # range(4) -> 3
snake_position = RIGHT
food = None
score = 0


def init_world(width: int, height: int) -> None:
    world.append([HASHTAG_ICON for _ in range(width)])
    for _ in range(height - 3):
        world.append([HASHTAG_ICON, *[' ' for _ in range(width - 2)], HASHTAG_ICON])
    world.append([HASHTAG_ICON for _ in range(width)])


def show_food(width: int, height: int) -> bool:
    global food
    global score

    if food is None:
        score -= 1
    food = randint(1, height - 3), randint(1, width - 2)
    if food not in snake:
        world[food[0]][food[1]] = FOOD_ICON
        return True
    return False


def append_deque(obj: deque, value, is_right: bool = True):
    obj.append(value) if is_right else obj.appendleft(value)


def append_to_snake(x: int, y: int, is_right: bool = True) -> None:
    if snake_position == RIGHT:
        append_deque(snake, (x, y + 1), is_right)
    elif snake_position == LEFT:
        append_deque(snake, (x, y - 1), is_right)
    elif snake_position == UP:
        append_deque(snake, (x - 1, y), is_right)
    elif snake_position == DOWN:
        append_deque(snake, (x + 1, y), is_right)


def game_state(console: Console, width: int, height: int) -> bool:
    global score

    snake_head = snake[len(snake) - 1]
    if snake_head[0] == 0 or snake_head[0] + 2 == height \
            or snake_head[1] == 0 or snake_head[1] + 1 == width \
            or 1 < snake.count(snake_head):
        console.write_line("\nYou crashed!!!", fore_color=Fore.RED, text_style=Style.BRIGHT, count=2)
        return False

    if snake_head == food or food is None:
        if show_food(width, height):
            score += 1
            append_to_snake(*snake_head, is_right=False)

    console.clear_console()

    x_, y_ = None, None
    removed_place_x, removed_place_y = snake.popleft()
    world[removed_place_x][removed_place_y] = ' '
    for x, y in snake.copy():
        world[x][y] = SNAKE_ICON
        x_, y_ = x, y
    append_to_snake(x_, y_)

    connected_rows = map(lambda row: ''.join(row), world)
    console.write_line(''.join(connected_rows))
    console.write(f"Score: {score}")

    return True


def get_console_position(console: Console) -> tuple:
    monitor_width, monitor_height = get_system_metrics()
    _, _, console_width, console_height = console.rect.refresh()
    return (monitor_width - console_width) // 2, (monitor_height - console_height) // 2


def main():
    global world
    global snake
    global snake_position
    global score
    global food

    init_colorama()  # Init colorama for coloring texts in console

    # Define console
    console = Console()
    console.title = "Snake Game 🐍"  # Change console title.
    console.change_terminal_size(
        60, 20
    )  # Change console size to 90 columns and 30 lines.
    console_position = get_console_position(console)
    console.rect.move_to(*console_position)  # centered console
    width, height = console.terminal_columns, console.terminal_lines

    def change_snake_position(key):
        if key in [Key.right, Key.left, Key.up, Key.down]:
            global snake_position
            positions = {
                Key.right: RIGHT,
                Key.left: LEFT,
                key.up: UP,
                Key.down: DOWN,
            }
            d = positions.get(key)
            if (d == RIGHT and snake_position == LEFT) or (d == UP and snake_position == DOWN) or \
                    (d == LEFT and snake_position == RIGHT) or (d == DOWN and snake_position == UP):
                return None
            snake_position = d

    listener = Listener(on_press=change_snake_position)
    listener.start()

    # Game Loop
    while True:
        init_world(width, height)  # Put all initial world characters in a list. [Char By Char]
        while game_state(console, width, height):
            console.sleep_(.1)
        else:
            console.get_input("Press Enter to continue...")
            world = list()
            snake = deque([(5, i + 5) for i in range(4)])  # range(4) -> 3
            snake_position = RIGHT
            score = 0
            food = None


if __name__ == '__main__':
    main()
