"""
Wordle Clone 
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from pathlib import Path
from random import randint

class Vault():

    def __init__(self) -> None:
        self.guess_list, self.allowed_guesses = self.getGuessData()
        self.setGuessWord()
        
    def getGuessData(self):
        resources_folder = Path(__file__).joinpath("../resources")
        guesses = open(resources_folder.joinpath("guesses.txt"), 'r').readlines()
        allowed_guesses = open(resources_folder.joinpath("allowedguesses.txt"), 'r').readlines()

        for i in range(len(guesses)):
            guesses[i] = guesses[i].replace('\n', '')
        
        for i in range(len(allowed_guesses)):
            allowed_guesses[i] = allowed_guesses[i].replace('\n', '')

        return guesses, allowed_guesses

    def validate_guess(self, guess):
        
        invalid_title = "Invalid Guess"
    
        if len(guess) < 5:
            return [False, {'invalid_title': invalid_title, 'invalid_body':'Guess length should be equal to 5!\n'}]

        if not guess.isalpha() :
            return [False, {'invalid_title': invalid_title, 'invalid_body':'Guess should only be comprised of letters in the English alphabet!\n'}]

        if guess not in self.allowed_guesses:
            return [False, {'invalid_title': invalid_title, 'invalid_body':'Guess not allowed!\n'}]

        return [True]

    def setGuessWord(self):
        self.secretWord = self.guess_list[randint(0, len(self.guess_list)-1)]

    def getSecret(self):
        return self.secretWord
        

class Game():

    def __init__(self, gridsize, wordsize, interactables ) -> None:
        self.gridsize = gridsize
        self.wordsize = wordsize
        self.current_guess_count = 0
        self.isGameOver = False
        self.isWin = False
        
        self.vault = Vault() 

        self.row_boxes = interactables['row_boxes']
        self.get_guess_input = interactables['guess_input']
        self.show_dialog = interactables['show_dialog']
        self.used_letter = interactables['used_letter']
    
    def do_guess(self):
        if self.isGameOver:
            return

        localSecret = self.vault.getSecret()
        guess = self.get_guess_input()
        score = 0
        
        validatorCheck = self.vault.validate_guess(guess)
        
        if not validatorCheck[0]:
            error_message = validatorCheck[1]
            self.show_dialog(error_message['invalid_title'], error_message['invalid_body'], 0)
            return 

        
        for i in range(self.wordsize):
            current_box = self.row_boxes[self.current_guess_count].children[i]
            current_box.label = guess[i].upper()
            current_box.style.background_color = '#A9A9A9'
            self.used_letter(guess[i], '#696969')
            

            if guess[i] == localSecret[i]:
                localSecret = localSecret[:i] + '!' + localSecret[i+1:]
                guess = guess[:i] + '?' + guess[i+1:]
                self.used_letter(guess[i], '#90EE90')
                current_box.style.background_color = '#90EE90'
                score += 1

        for i in range(self.wordsize):
            current_box = self.row_boxes[self.current_guess_count].children[i]
            if guess[i] in localSecret:
                localSecret = localSecret.replace(guess[i], '!')
                current_box.style.background_color = '#FFFF33'
                self.used_letter(guess[i], '#FFFF33')

        if score == self.wordsize:
            self.isGameOver = True
            self.isWin = True
            self.show_dialog("Game Over!", "You won! Pasikat ka na sa Twitter!\nClick reset to play again", 1)

        self.current_guess_count += 1
        if self.current_guess_count > 5 and not self.isWin:
            self.isGameOver = True
            self.show_dialog("Game Over!", f"You used up all your guesses.\nThe secret word was {self.vault.getSecret().upper()} \nClick reset to play again :(", 1)

        return
    
    def resetGame(self):
        self.current_guess_count = 0
        self.isWin = False
        self.isGameOver = False
        self.vault.setGuessWord()

        return 

class WordleClone(toga.App):

    def startup(self):
        #SET VALUES
        self.gridsize = 6 # nxn grid
        self.wordsize = 5
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        for attr in dir(self):
            print(attr)
        
        # Generate UI
        self.generate_ui()

        # Start Game
        self.start_game()

    def start_game(self):
        interactables = {
            'guess_input': self.get_guess_input,
            'row_boxes': self.row_boxes,
            'show_dialog': self.show_dialog,
            'used_letter': self.used_letter
        }

        self.Game = Game(self.gridsize, self.wordsize, interactables)

    def generate_ui(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, alignment="center"))
        
        guess_label = toga.Label('Your guess: ', style=Pack(padding=5))
        self.guess_input = toga.TextInput(style=Pack(flex=1))

        guess_box = toga.Box(style=Pack(direction=ROW, padding=(5,0)))
        guess_box.add(guess_label)
        guess_box.add(self.guess_input)
        
        button = toga.Button('Guess!', on_press=self.do_guess_handler, style=Pack(padding=(5,0)))

        self.alphaBox = toga.Box(style=Pack(alignment='center', padding=(5,0)))
        for letter in self.alphabet:
            alphabet_label = toga.Label(letter, style=Pack(padding=(5,0), alignment='center', font_size='12', background_color='#696969', color='#FAF9F6'))
            self.alphaBox.add(alphabet_label)

        resetButton = toga.Button('Restart', on_press=self.reset_game_handler, style=Pack(padding=(5,0)))

        main_box.add(guess_box)
        main_box.add(button)
        main_box.add(self.alphaBox)
        main_box.add(self.guess_area_gen())
        main_box.add(resetButton)
        
        self.main_window = toga.MainWindow(title=self.formal_name, size=(600, 500))
        self.main_window.content = main_box
        self.main_window.show()


    def guess_area_gen(self):
        guess_area = toga.Box(style=Pack(direction=COLUMN, padding=0, flex=1, alignment="center"))
        self.row_boxes = [toga.Box(style=Pack(direction=ROW, padding=2, flex=1, alignment="center")) for i in range(self.gridsize)] #create 6 rows
        
        for i in range(self.gridsize):
            for j in range(self.wordsize):
                newButton = toga.Button(label="", id=f"{j}", style=Pack(background_color="#FAF9F6", font_family='monospace', font_weight='bold', padding_left=5, padding_right=5, width=50, height=50), enabled=False)
                self.row_boxes[i].add(newButton)

            guess_area.add(self.row_boxes[i])

        return guess_area
    
    def reset_ui(self):
        #clear contents 
        for i in range(self.gridsize):
            for j in range(self.wordsize):
                self.row_boxes[i].children[j].style.background_color = "#FAF9F6"
                self.row_boxes[i].children[j].label = ""

        #reset hints
        for i in range(len(self.alphabet)):
            self.alphaBox.children[i].style.color = '#FAF9F6'

        return

    def show_dialog(self, title, message, messageType):
        if messageType == 0:
            self.main_window.error_dialog(title=title, message=message)
        if messageType == 1:
            self.main_window.info_dialog(title=title, message=message)
        return

    def used_letter(self, letter, color):
        for i in range(len(self.alphabet)):
            if self.alphabet[i].lower() == letter:
                self.alphaBox.children[i].style.color = color
        return


    def get_guess_input(self):
        guess = self.guess_input.value.lower()
        self.guess_input.value = ""
        return guess

    def do_guess_handler(self, widget):
        return self.Game.do_guess()
        
    def reset_game_handler(self, widget):
        self.reset_ui()
        return self.Game.resetGame()

        
def main():
    return WordleClone()
