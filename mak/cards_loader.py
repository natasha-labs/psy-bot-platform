import os
import random


def load_cards(base_path="assets/mak_cards"):
    decks = {}

    if not os.path.exists(base_path):
        return decks

    for deck_name in os.listdir(base_path):
        deck_path = os.path.join(base_path, deck_name)

        if not os.path.isdir(deck_path):
            continue

        images = []
        for file in os.listdir(deck_path):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(os.path.join(deck_path, file))

        if images:
            decks[deck_name] = images

    return decks


def get_random_card(decks, deck_name=None):
    if not decks:
        return None, None

    if deck_name and deck_name in decks:
        chosen_deck = deck_name
    else:
        chosen_deck = random.choice(list(decks.keys()))

    card = random.choice(decks[chosen_deck])
    return chosen_deck, card
