"""
Wordle Clone 
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from pathlib import Path
from random import randint


class WordleClone(toga.App):

    def startup(self):
        #SET VALUES
        self.gridsize = 6 # nxn grid
        self.wordsize = 5
        self.current_guess_count = 0
        self.isGameOver = False
        self.isWin = False
        self.guess_list, self.allowed_guesses = self.get_guess_data()
        # Generate UI
        self.generate_ui()
        self.setGuessWord()

    def setGuessWord(self):
        self.secretWord = self.guess_list[randint(0, len(self.guess_list)-1)]
        print(self.secretWord)

    def get_guess_data(self):
        resources_folder = Path(__file__).joinpath("../resources")
        guesses = open(resources_folder.joinpath("guesses.txt"), 'r').readlines()
        allowed_guesses = open(resources_folder.joinpath("allowedguesses.txt"), 'r').readlines()

        for i in range(len(guesses)):
            guesses[i] = guesses[i].replace('\n', '')
        
        for i in range(len(allowed_guesses)):
            allowed_guesses[i] = allowed_guesses[i].replace('\n', '')

        return guesses, allowed_guesses

    def generate_ui(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, alignment="center"))
        
        guess_label = toga.Label(
            'Your guess: ',
            style=Pack(padding=5)
        )
        self.guess_input = toga.TextInput(style=Pack(flex=1))

        guess_box = toga.Box(style=Pack(direction=ROW, padding=(5,0)))
        guess_box.add(guess_label)
        guess_box.add(self.guess_input)
        
        button = toga.Button('Guess!', on_press=self.do_guess, style=Pack(padding=(5,0)))

        alphaBox = toga.Box(style=Pack(alignment='center', padding=(2,0)))
        alphabet_label = toga.Label('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z', style=Pack(padding=(3,0), alignment='center', font_family='monospace', font_size='12'))
        alphaBox.add(alphabet_label)

        resetButton = toga.Button('Restart', on_press=self.resetGame, style=Pack(padding=(5,0)))

        main_box.add(guess_box)
        main_box.add(button)
        main_box.add(alphaBox)
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

    def do_guess(self, widget):
        localSecret = self.secretWord
        guess = self.guess_input.value.lower()
        self.guess_input.value = ""
        
        if not self.validate_guess(guess) or self.isGameOver:
            return 

        score = 0
        for i in range(self.wordsize):
            current_box = self.row_boxes[self.current_guess_count].children[i]
            current_box.label = guess[i].upper()
            current_box.style.background_color = '#A9A9A9'
            if guess[i] == localSecret[i]:
                localSecret = localSecret[:i] + '!' + localSecret[i+1:]
                guess = guess[:i] + '?' + guess[i+1:]
                current_box.style.background_color = '#90EE90'
                score += 1

        for i in range(self.wordsize):
            current_box = self.row_boxes[self.current_guess_count].children[i]
            if guess[i] in localSecret:
                localSecret = localSecret.replace(guess[i], '!')
                current_box.style.background_color = 'orange'

        if score == self.wordsize:
            self.isGameOver = True
            self.isWin = True
            self.show_dialog("Game Over!", "You won! Pasikat ka na sa Twitter!\nClick reset to play again", 1)

            

        self.current_guess_count += 1
        if self.current_guess_count > 5 and not self.isWin:
            self.isGameOver = True
            self.show_dialog("Game Over!", "You used up all your guesses.\nClick reset to play again :(", 1)

        return


    def validate_guess(self, guess):
        invalid_guess_message= "Invalid Guess"
        
        if len(guess) < 5:
            self.show_dialog(invalid_guess_message, 'Guess length should be equal to 5!', 0)
            return False

        if not guess.isalpha() :
            self.show_dialog(invalid_guess_message, 'Guess should only be comprised of letters in the English alphabet!', 0)
            return False

        if guess not in self.allowed_guesses:
            self.show_dialog(invalid_guess_message, 'Guess not allowed!', 0)
            return False

        return True 

    
    
    def show_dialog(self, title, message, messageType):
        if messageType == 0:
            self.main_window.error_dialog(title=title, message=message)
        if messageType == 1:
            self.main_window.info_dialog(title=title, message=message)
        return

    def resetGame(self, widget):
        self.current_guess_count = 0

        #clear contents 
        for i in range(self.gridsize):
            for j in range(self.wordsize):
                self.row_boxes[i].children[j].style.background_color = "#FAF9F6"
                self.row_boxes[i].children[j].label = ""

        self.isWin = False
        self.isGameOver = False

        self.setGuessWord()
        return

        
def main():
    return WordleClone()
