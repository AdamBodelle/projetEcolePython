import pygame  # type: ignore
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 40
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BRAVO_FONT_SIZE = 80  # Font size for "BRAVO!" and "GAME OVER"
SCORE_FILE = "score.txt"  # File to store the score

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)  # Gold for the score text
RED = (255, 0, 0)  # Red for "Game Over"
BUTTON_TEXT_COLOR = GOLD  # Color for button text

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Screens")

# Load background image
background = pygame.image.load("resource/image/maison.jpg")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load custom font
simpson_font = pygame.font.Font("resource/Font/Homer_Simpson_Revised.ttf", FONT_SIZE)
big_font = pygame.font.Font("resource/Font/Homer_Simpson_Revised.ttf", BRAVO_FONT_SIZE)

# Buttons positions
replay_button_rect = pygame.Rect((SCREEN_WIDTH // 2 - BUTTON_WIDTH - 20, SCREEN_HEIGHT - 150), (BUTTON_WIDTH, BUTTON_HEIGHT))
menu_button_rect = pygame.Rect((SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 150), (BUTTON_WIDTH, BUTTON_HEIGHT))

# Ensure SCORE_FILE exists and contains valid data
if not os.path.exists(SCORE_FILE) or not open(SCORE_FILE).readlines()[0]:
    with open(SCORE_FILE, "w") as file:
        file.write("0")  # Initialize score to 0 if file is missing or invalid

# Function to load the score from a file
def load_score():
    with open(SCORE_FILE, "r") as file:
        content = file.readlines()  # Read and clean content
        if content[0]:  # Check if the content is a valid number
            return content
        else:
            print(f"Invalid score file content: '{content}'. Resetting score to 0.")
            return 0

# Function to save the score to a file
def save_score(score):
    with open(SCORE_FILE, "a") as file:
        file.write(str(score)+'\n')

# Load initial score
score = load_score()

# Function to draw the "Bravo" screen
def draw_bravo_screen():
    screen.blit(background, (0, 0))

    bravo_text = big_font.render("BRAVO!", True, GOLD)
    bravo_rect = bravo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(bravo_text, bravo_rect)

    score_text = simpson_font.render(f"Score : {score}", True, GOLD)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(score_text, score_rect)

    replay_text = simpson_font.render("Rejouer", True, BUTTON_TEXT_COLOR)
    menu_text = simpson_font.render("Menu", True, BUTTON_TEXT_COLOR)

    replay_text_rect = replay_text.get_rect(center=replay_button_rect.center)
    menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)

    screen.blit(replay_text, replay_text_rect)
    screen.blit(menu_text, menu_text_rect)

# Function to draw the "Game Over" screen
def draw_game_over_screen():
    screen.blit(background, (0, 0))

    game_over_text = big_font.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(game_over_text, game_over_rect)

    score_text = simpson_font.render(f"Score : {score}", True, RED)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(score_text, score_rect)

    replay_text = simpson_font.render("Rejouer", True, BUTTON_TEXT_COLOR)
    menu_text = simpson_font.render("Menu", True, BUTTON_TEXT_COLOR)

    replay_text_rect = replay_text.get_rect(center=replay_button_rect.center)
    menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)

    screen.blit(replay_text, replay_text_rect)
    screen.blit(menu_text, menu_text_rect)

# Main loop
def main():
    global current_screen, score

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button_rect.collidepoint(event.pos):
                    score += 10  # Example: Increment score on replay
                    save_score(score)  # Save the new score
                    current_screen = "bravo"  # Example: Reset to victory screen
                elif menu_button_rect.collidepoint(event.pos):
                    print("Return to main menu!")
                    pygame.quit()
                    sys.exit()

        # Render the current screen
        if current_screen == "bravo":
            draw_bravo_screen()
        elif current_screen == "game_over":
            draw_game_over_screen()

        pygame.display.flip()

# Run the game
if __name__ == "__main__":
    current_screen = "bravo"  # Default to "bravo" screen for testing
    main()




