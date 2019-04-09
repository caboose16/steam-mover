import os
import re
import shutil
from prettytable import PrettyTable
from hurry.filesize import size
from hurry.filesize import alternative
from Game import Game

class SteamLibrary:
    def __init__(self):
        self.steam_dir = 'C:\\Program Files (x86)\\Steam'
        self.steamapp_dir = self.steam_dir + '\\steamapps'
        self.library_dir = list()
        self.game_list = list()

        self.get_game_dir()
        self.add_games()

    # Get game directory and put them as a key in a dict that is in a list
    def get_game_dir(self):
        temp_game_dir = self.steamapp_dir
        self.library_dir.append(temp_game_dir) # index 0 is first dir
        self.game_list.append(list()) # index 0 is a list for games of first dir

        # for each new steam game folder found a new dir and game list are added to library_dir and game_list
        library = self.steam_dir + '\\steamapps\\libraryfolders.vdf' # libraryfolder.vdf contains all steam game folders
        file = open(library, 'r')
        for line in file:
            line_values = re.findall('"([^"]*)"', line)
            if (len(line_values) > 0):
                if line_values[0].isdigit():
                    temp_game_dir = line_values[1].replace('\\\\', '\\') + '\\steamapps'
                    self.library_dir.append(temp_game_dir)
                    self.game_list.append(list())

        # Adds app manifests from given directory to game_list
    def add_games(self):
        for dir_, glist in zip(self.library_dir, self.game_list):
            if not os.path.exists(dir_):
                print('Error: Could not find path ' + dir_)
                return

            for file in os.listdir(dir_):
                if file.endswith('.acf'):
                    game = Game(file, dir_)

                    # Retrieve and add game name and install_dir
                    path = dir_ + '\\' + game.app_manifest
                    file = open(path, 'r') 
                    lines = file.readlines()
                    if len(lines) >= 4:
                        name = lines[4]
                        game.name = re.findall('"([^"]*)"', name)[1]
                        install_dir = lines[6]
                        game.install_dir = re.findall('"([^"]*)"', install_dir)[1]
                        size = lines[9]
                        game.size = int(re.findall('"([^"]*)"', size)[1])

                        glist.append(game)

    # TODO: Make funnction that moves game from one directory to another
    # Userinput '[src_dir#] [des_dir#] [appid]'
    def move_games(self, userInput):
        print()
        arguments = userInput.split(' ')
        try:
            src = int(arguments[0])
            des = int(arguments[1])
        except ValueError:
            print('Error 1: Invalid number for source or destination')
            return
        if (src > len(self.library_dir)) or (des > len(self.library_dir)):
            print('Error 2: Invalid number for source or destination')
        if (src < 0) or (des < 0):
            print('Error 3: Invalid number for source or destination')

        src_dir = self.library_dir[src]
        des_dir = self.library_dir[des]
        appid_list = arguments[2:]

        print("Searching for Game(s)")

        for game in appid_list:
            found = False
            if game.isdigit():
                for g in self.game_list[src]:
                    if g.appid == game:
                        found = True
                        print('Found ' + g.name + '! Do Not Close Program!')
                        print('Copying game folder. This may take a while depending on size.')
                        shutil.move(src_dir + '\\' + g.app_manifest, des_dir + '\\' + g.app_manifest)
                        shutil.move(src_dir + '\\common\\' + g.install_dir, des_dir + '\\common\\' + g.install_dir)
                        print('Succesfully moved ' + g.name + ' from ' + src_dir + ' to ' + des_dir)
                        print()

                        # TODO: Move game from 1 game list to another
                        self.game_list[des].append(g)
                        self.game_list[src].remove(g)
                        break
                if not found:
                    print('Error: Could not find App ID ' + game + ' in ' + src_dir)
            else:
                print('Error: Invalid Input "' + game + '"')
        
        print('Restart Steam for changes to apply.')

    # Print Game List
    def print_game_list(self):
        x = -1

        print('---Games---')

        for dir_, dir2 in zip(self.game_list, self.library_dir):
            x += 1
            t = PrettyTable(['App ID', 'App Name', 'Size'])
            t.align = 'l'
            t.align['Size'] = 'r'
            for game in dir_:
                t.add_row([game.appid, game.name, size(game.size, system=alternative)])
            t.sortby = 'App Name'

            print('---Dir ' + str(x) + ' - ' + dir2[0:2] + '---')
            print(t)

mySL = SteamLibrary()
mySL.print_game_list()

while True:
    print('Enter game(s) to move or "quit": [src_dir#] [des_dir#] [appid]')
    user_input = input()
    if (user_input == 'exit') or (user_input == 'quit') or (user_input == 'q'):
        quit()
    else:
        mySL.move_games(user_input)
        user_input = input()
        while True:
            print('Continue? (y)es/(n)o')
            if (user_input.lower() == 'n') or (user_input.lower() == 'no'):
                quit()
            elif (user_input.lower() == 'y') or (user_input.lower() == 'yes'):
                break
            else:
                print('Error 4: Invalid Input')
        print()
        mySL.print_game_list()