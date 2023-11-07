# imports

import os
import requests
from PIL import Image


# Fetch necessary lists for team builder
if os.path.exists('./functional_data/') is not True:
    os.mkdir('./functional_data/')

if os.path.exists('./functional_data/full_pokemon_list.txt') is not True:
    # get all pokemon
    r = requests.get('https://pokeapi.co/api/v2/pokemon/?limit=2000')
    if r.status_code == 404:
        print('Could not fetch pokemon list')
    elif r.status_code == 200:
        r = r.json()
        with open('./functional_data/full_pokemon_list.txt', 'w', encoding='utf-8') as f:
            for entry in r['results']:
                name = entry['name']
                f.write(f'{name}\n')


if os.path.exists('./functional_data/full_item_list.txt') is not True:
    # get all items
    r = requests.get('https://pokeapi.co/api/v2/item/?limit=2500')
    if r.status_code == 404:
        print('Could not fetch item list')
    elif r.status_code == 200:
        r = r.json()
        with open('./functional_data/full_item_list.txt', 'w', encoding='utf-8') as f:
            for entry in r['results']:
                name = entry['name']
                f.write(f'{name}\n')

if os.path.exists('./functional_data/icons') is not True:
    # get all type icons
    os.mkdir('./functional_data/icons')
    icons = ['bug', 'dark', 'dragon', 'electric', 'fairy',
             'fighting', 'fire', 'flying', 'ghost', 'grass', 'ground',
             'ice', 'normal', 'poison', 'psychic', 'rock', 'steel', 'water']
    for item in icons:
        with open(f'./functional_data/icons/{item}.png', 'wb') as f:
            f.write(requests.get(f'https://raw.githubusercontent.com/kelseymosh/pokemon-team-builder/main/public/assets/{item}.png').content)
    with open(f'./functional_data/icons/pokedex.png', 'wb') as f:
        f.write(requests.get(f'https://archives.bulbagarden.net/media/upload/3/37/RG_Pok%C3%A9dex.png').content)
    image = Image.open('./functional_data/icons/pokedex.png')
    image = image.resize((25, 25))
    image.save('./functional_data/icons/pokedex.png')






