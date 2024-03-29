import requests
from time import sleep
import os


def crash_on_error(response):
    """
    Function used to raise exception and end client work.
    :param response: Response object with answer from rest api game server
    """
    if response.status_code != 200:
        raise Exception(f"Something goes wrong. Server respond with: {response.status_code}")


def main(input_foo=input, print_foo=print):
    """
    Function used to control all client setup flow & logic
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    """
    host = "127.0.0.1:5000"
    print_foo("Welcome to Macau Game!")
    host = find_server(host, input_foo, print_foo)
    process = {'c': create_game, 'j': join_game, 'w': watch_game}
    create_join_watch = input_foo("Do you want to Create game, Join existing one or Watch? (c/j/w): ").lower()
    if create_join_watch in process:
        process[create_join_watch](host, input_foo, print_foo)
    else:
        print_foo(f"Wrong option: {create_join_watch}")


def find_server(host, input_foo, print_foo):
    """
    Function used to check connection with server.
    :param host: string with address to game server in IP:PORT format
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    :return: checked and correct string with address to working server
    """
    while True:
        try:
            response = requests.get(f"http://{host}/")
            if response.status_code == 200:
                print_foo("Connection to Game Server checked.")
                break
        except requests.exceptions.ConnectionError as ex:
            print_foo(f'Exception: {ex}')
            print_foo(f"Game Server at {host} are not responding.")
            host = input_foo("Enter host address in IP:PORT format: ")
    return host


def find_game(host, input_foo, print_foo):
    """
    Function used to check if game with given game id exists on game server
    :param host: string with address to game server in IP:PORT format
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    :return: integer with correct game_id, integer with response status code 200,
     list of string with not yet logged players
    """
    status_code = 404
    game_id = -1
    waiting_for = []
    while status_code != 200:
        game_id = int(input_foo("Enter ID of the game: "))
        response = requests.get(f"http://{host}/macau/{game_id}/state")
        status_code = response.status_code
        if status_code != 200:
            print_foo("Game ID not valid.")
        else:
            waiting_for = response.json()['state']['waiting_for']
    return game_id, status_code, waiting_for


def watch_game(host, input_foo, print_foo):
    """
    Function used to connect to game on server as a spectator.
    :param host: string with address to game server in IP:PORT format
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    """
    print_foo("Watching existing game!")
    game_id, status_code, _ = find_game(host, input_foo, print_foo)
    os.system("cls || clear")
    print_foo("Game ID correct. Game events will appear below:")
    last_show = None
    while status_code == 200:
        response = requests.get(f"http://{host}/macau/{game_id}")
        crash_on_error(response)
        to_show = response.json()['output']
        if last_show != to_show:
            for line in to_show:
                print_foo(line)
            last_show = to_show
        if 'Game won by' in to_show[-1]:
            break
        sleep(0.5)


def join_game(host, input_foo, print_foo):
    """
    Function used to connect to existing game on server as a guest.
    :param host: string with address to game server in IP:PORT format
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    """
    print_foo("Joining existing game!")
    game_id, status_code, waiting_for = find_game(host, input_foo, print_foo)
    print_foo("Game ID correct.")
    message = 'Waiting for players: '
    for name in waiting_for:
        message += f'{name}, '
    print_foo(message[:-2])
    my_name = input_foo("Enter your name: ")
    game_loop(game_id, my_name, host, input_foo, print_foo)


def create_game(host, input_foo, print_foo):
    """
    Function used to create new game on game server and connect to it as a owner.
    :param host: string with address to game server in IP:PORT format
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    """
    print_foo("Creating new Macau Game!")
    how_many_players = int(input_foo("Enter number of players: "))
    if how_many_players < 2:
        raise Exception('Wrong number of players entered!')
    how_many_cards = int(input_foo('How many cards on start?: '))
    if how_many_cards < 3:
        raise Exception('Wrong number of starting cards entered!')
    names = []
    my_name = input_foo('Enter your name: ')
    names.append(my_name)
    for index in range(2, how_many_players + 1):
        name = input_foo(f'Enter name for player#{index}: ')
        names.append(name)
    json_data = {'how_many_cards': how_many_cards, 'players_names': names}
    response = requests.post(f"http://{host}/macau", json=json_data)
    crash_on_error(response)
    game_id = response.json()['game_id']
    print_foo(f"Game created. Game ID: {game_id}")
    _ = input_foo("Confirm ID by pressing Enter...")
    game_loop(game_id, my_name, host, input_foo, print_foo)


def game_loop(game_id, my_name, host, input_foo=input, print_foo=print):
    """
    Function used to control input/output game loop with client-server
    :param game_id: integer with correct game id of game existing on game server
    :param my_name: string with name of rest api client user
    :param host: string with address to game server in IP:PORT format
    :param input_foo: functor with function used to get input from user
    :param print_foo: functor with function used to show output to user
    """
    questions = [
        "Which card(s) from your hand do you want to play?:",
        "Enter VALUE of requested cards:",
        "Enter COLOR of requested cards:"
    ]
    response = requests.get(f"http://{host}/macau/{game_id}/{my_name}/key")
    crash_on_error(response)
    token = response.json()['access_token']
    print_foo(f"User {my_name} correctly logged. Wait for your move...")
    last_output = []
    while True:
        response = requests.get(f"http://{host}/macau/{game_id}/{my_name}?access_token={token}")
        crash_on_error(response)
        output = response.json()['output']
        if output != last_output:
            response = requests.get(f"http://{host}/macau/{game_id}")
            crash_on_error(response)
            to_show = response.json()['output']
            if questions[1] in output[-1] or questions[2] in output[-1]:
                to_show.append(output[-3])
            os.system("cls || clear")
            action = False
            for line in to_show:
                print_foo(line)

            for question in questions:
                if question in output[-1]:
                    move = input_foo(output[-1])
                    response = requests.post(
                        f"http://{host}/macau/{game_id}/{my_name}?player_move={move}&access_token={token}"
                    )
                    crash_on_error(response)
                    action = True
                    break
            if "Game won by" in output[-1]:
                print_foo(output[-1])
                break

            if not action:
                print_foo("Waiting for other player move...")
            last_output = output
        sleep(0.05)


if __name__ == "__main__":
    main()
