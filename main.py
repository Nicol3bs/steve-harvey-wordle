import random
import sys
import wordle_ui
from blessed import Terminal

term = Terminal()

def parse_words(raw_text):
    """Task 1a: Return a list of cleaned, uppercase 5-letter words from raw_text."""
    words = []
    for line in raw_text.splitlines():
        word = line.strip().upper()
        if len(word) == 5:
            words.append(word)
    return words

def get_secret_word(word_list, previous_secret=None):
    """Task 1b: Return custom user word if valid, otherwise return a random word."""
    custom_word = wordle_ui.prompt_secret_word()
    if custom_word:
        custom_word = custom_word.strip().upper()

        if (
            len(custom_word) == 5
            and custom_word in word_list
            and custom_word != previous_secret
        ):
            return custom_word

    available_words = [word for word in word_list if word != previous_secret]
    return random.choice(available_words or word_list)

def get_valid_guess(word_list, guessed_words):
    """Task 2: Loop until user enters a valid, unguessed 5-letter word."""
    while True:
        guess = wordle_ui.prompt_guess()
        guess = guess.strip().upper()

        if len(guess) != 5:
            wordle_ui.show_message("Word must have 5 letters.")
        elif guess not in word_list:
            wordle_ui.show_message("Word is not in the word list")
        elif guess in guessed_words:
            wordle_ui.show_message("You already guessed that word.")
        else:
            return guess


def evaluate_guess(guess, secret_word):
    """Task 3: Return a 5-character string of 'G', 'Y', and 'B' handling duplicates."""
    feedback = ["B"] * len(guess)
    remaining = {}

    for letter in secret_word:
        remaining[letter] = remaining.get(letter, 0) + 1

    for index, letter in enumerate(guess):
        if letter == secret_word[index]:
            feedback[index] = "G"
            remaining[letter] -= 1

    for index, letter in enumerate(guess):
        if feedback[index] != "G" and remaining.get(letter, 0) > 0:
            feedback[index] = "Y"
            remaining[letter] -= 1

    return "".join(feedback)

def update_keyboard(keyboard, guess, feedback):
    """Task 4: Upgrade keyboard dictionary statuses ('G' > 'Y' > 'B' > 'U')."""
    status_rank = {"U": 0, "B": 1, "Y": 2, "G": 3}
    for letter, status in zip(guess, feedback):
        if status_rank[status] > status_rank[keyboard[letter]]:
            keyboard[letter] = status

def print_board(guessed_words, feedback_history, keyboard):
    """Task 5: Use blessed to render the 6x5 grid and call wordle_ui.print_keyboard()."""
    wordle_ui.print_header()
    for row in range(6):
        if row < len(guessed_words):
            tiles = []
            for letter, status in zip(guessed_words[row], feedback_history[row]):
                if status == "G":
                    tiles.append(term.black_on_green(letter))
                elif status == "Y":
                    tiles.append(term.black_on_yellow(letter))
                else:
                    tiles.append(term.white_on_lightslategray(letter))
            print(" ".join(tiles))
        else:
            print("_ _ _ _ _")
    wordle_ui.print_keyboard(keyboard)

def play_round(word_list, previous_secret=None):
    """Task 6: Main 6-attempt game loop."""
    secret_word = get_secret_word(word_list, previous_secret)
    guessed_words = []
    feedback_history = []
    keyboard = wordle_ui.init_keyboard()

    print_board(guessed_words, feedback_history, keyboard)

    for _ in range(6):
        guess = get_valid_guess(word_list, guessed_words)
        feedback = evaluate_guess(guess, secret_word)
        guessed_words.append(guess)
        feedback_history.append(feedback)
        update_keyboard(keyboard, guess, feedback)
        print_board(guessed_words, feedback_history, keyboard)

        if guess == secret_word:
            wordle_ui.show_message("Congratulations! You guessed the word!", is_error=False)
            return secret_word

    wordle_ui.show_message(
        f"Game over! The secret word was {secret_word}.",
        is_error=True,
    )
    return secret_word

def run_tests():
    """Unit tests for Task 3."""
    assert evaluate_guess("CRANE", "CRANE") == "GGGGG"
    assert evaluate_guess("LIGHT", "CRANE") == "BBBBB"
    assert evaluate_guess("TRACE", "CRANE") == "BGGYG"
    assert evaluate_guess("SPEED", "ABIDE") == "BBYBY"
    assert evaluate_guess("ULLAL", "SKILL") == "BYBBG"
    assert evaluate_guess("EERIE", "APPLE") == "BBBBG"
    assert evaluate_guess("EERIE", "ERASE") == "GBYBG"
    print("All tests passed!")

def main():
    if "--test" in sys.argv:
        run_tests()
        return
    word_list = parse_words(wordle_ui.RAW_WORD_DATA)
    previous_secret = None
    while True:
        previous_secret = play_round(word_list, previous_secret)
        if not wordle_ui.prompt_play_again():
            break

if __name__ == "__main__":
    main()
    