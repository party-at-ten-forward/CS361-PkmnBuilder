# ~~~~~~~ import libs ~~~~~~
import streamlit as st
import zmq
import subprocess
import os
import time
import uuid
from PIL import Image


# ~~~~~~~ Web app init info ~~~~~~~~
st.set_page_config(
    page_title='Pokemon Team Builder!',
    page_icon='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png',
    layout='wide'
)

# ~~~~~~~ run first time setup if needed ~~~~~~~~~
if os.path.exists('./functional_data/') is not True:
    os.mkdir('./functional_data/')
if os.path.exists('./functional_data/has_run.txt') is not True:
    with st.spinner('Running First Time Setup, Please Wait!'):
        first_time_run = subprocess.Popen(['python3', './first_time_setup.py'])
        time.sleep(20)
        subprocess.Popen.terminate(first_time_run)
        with open('./functional_data/has_run.txt', 'w', encoding='utf-8') as f:
            f.write('First time setup ran successfully!')
    st.success('Done!')

# ~~~~~~~ import data ~~~~~~~

#  1 . import pokemon

with open('./functional_data/full_pokemon_list.txt', 'r', encoding='utf-8') as f:  # import pokemon
    pkmn_list = f.read()
    pkmn_list = pkmn_list.splitlines()

#  2 . import items
with open('./functional_data/full_item_list.txt', 'r', encoding='utf-8') as f:  # import items
    item_list = f.read()
    item_list = item_list.splitlines()


# ~~~~~~helper functions~~~~~~~~
@st.cache_data(experimental_allow_widgets=True)
def pokemon_data_fetcher(requested_pokemon: str):
    """take pokemon from option and fetch it. then parse out and return data"""
    # start zmq service
    pkmn_data_srvc = subprocess.Popen(['python3', './zmqServices/pokemon_data_service.py'])
    pokedex_srvc = subprocess.Popen(['python3', './zmqServices/pokedex_service.py'])

    # connect to zmq pokemon data service
    context = zmq.Context()

    socket1 = context.socket(zmq.REQ)
    socket1.connect("tcp://127.0.0.1:5555")
    socket1.send_pyobj(requested_pokemon)
    pkmn_received = socket1.recv_pyobj()

    socket2 = context.socket(zmq.REQ)
    socket2.connect("tcp://127.0.0.1:5556")

    # parse out data
    if pkmn_received == 'Could not find pokemon!':
        return 'Could not find pokemon!'
    else:
        try:
            # sprite
            sprite_url = pkmn_received['sprites']['front_default']
            # pokemon desc
            species_url = pkmn_received['species']['url']
            socket2.send_pyobj(species_url)
            species_received = socket2.recv_pyobj()
            flavor_list = species_received['flavor_text_entries']
            for item in flavor_list:
                if item['language']['name'] == "en":
                    dex_entry = item['flavor_text']
                    break
                else:
                    pass
            # species name
            species_name = species_received['name']
            # learnset
            learn_set = pkmn_received['moves']
            # type
            type_list = pkmn_received['types']
            types = []
            for item in type_list:
                types.append(item['type']['name'])
        except Exception:
            print('Unknown error!')

    # terminate zmq services
    subprocess.Popen.terminate(pkmn_data_srvc)
    subprocess.Popen.terminate(pokedex_srvc)

    return sprite_url, dex_entry, learn_set, types, species_name


def add_p_row(state_key):
    element_id = uuid.uuid4()
    st.session_state[f'{state_key}'].append(str(element_id))


def generate_p_row(full_pkmn_list, row_id: str):
    # Select Pokemon
    poke_col1, poke_col2 = st.columns([.65, .75])
    with poke_col1:
        pkmn_selection = st.selectbox("Select a Pokemon", full_pkmn_list, key=f'pkmn_{row_id}')
        poke_data = pokemon_data_fetcher(pkmn_selection)
        if poke_data[0] is None:
            st.write('Couldn\'t find sprite on PokeAPI.')
        else:
            st.image(poke_data[0])
        st.text("Type:")
        for item in poke_data[3]:
            image = Image.open(f'./functional_data/icons/{item}.png')
            new_image = image.resize((100, 20))
            st.image(new_image)
    with poke_col2:
        # display dex entry
        st.image(f'./functional_data/icons/pokedex.png')
        st.write(poke_data[1])
        # st.slider('Level', min_value=1, max_value=100, step=1, key=f'pkmn_lvl_{row_id}')
        # # try to find smogon link
        # st.write('Smogon Competitive Anaylsis:')
        # ver_selection = st.selectbox("Select a version",
        #                               ['RB', 'GS', 'RS',
        #                                'DP', 'BW', 'XY',
        #                                'SM', 'SS', 'SV'],
        #                               key=f'comp_analysis_{row_id}')
        # st.markdown(f'[Smogon Link](https://www.smogon.com/dex/{str.lower(ver_selection)}/pokemon/{[poke_data[4]]})')
    return {"PokeCol1": poke_col1, "PokeCol2": poke_col2}, poke_data

# ~~~~~~~~~ Layout stuff ~~~~~~~~~~


# Web App Header/Title
st.title('Pokemon Team Builder')
choice = st.selectbox('Team View Mode?', ('SinglePage', 'Tabbed'))

# init tabs session state
if 'tabs' not in st.session_state:
    st.session_state['tabs'] = ["Pokemon 1", "Pokemon 2", "Pokemon 3", "Pokemon 4", "Pokemon 5", "Pokemon 6"]

# init pkmn state session
if 'pkmn' not in st.session_state:
    st.session_state['pkmn'] = []

pkmn_collection = []


def tabbed(selection):
    if selection == 'Tabbed':
        # Teamslot display stuff
        tabs = st.tabs(st.session_state["tabs"])

        with tabs[0]:
            st.header("Teamslot 1")
            # Pokemon
            state_key_pkmn = 'pkmn'
            add_p_row(state_key_pkmn)
            pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][0])
            pkmn_collection.append(pokerow_data)
        with tabs[1]:
            st.header("Teamslot 2")
            # Select Pokemon
            add_p_row(state_key_pkmn)
            pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][1])
            pkmn_collection.append(pokerow_data)
        with tabs[2]:
            st.header("Teamslot 3")
            # Select Pokemon
            add_p_row(state_key_pkmn)
            pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][2])
            pkmn_collection.append(pokerow_data)
        with tabs[3]:
            st.header("Teamslot 4")
            # Select Pokemon
            add_p_row(state_key_pkmn)
            pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][3])
            pkmn_collection.append(pokerow_data)
        with tabs[4]:
            st.header("Teamslot 5")
            # Select Pokemon
            add_p_row(state_key_pkmn)
            pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][4])
            pkmn_collection.append(pokerow_data)
        with tabs[5]:
            st.header("Teamslot 6")
            # Select Pokemon
            add_p_row(state_key_pkmn)
            pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][5])
            pkmn_collection.append(pokerow_data)
    else:
        return


def single_page(selection):
    if selection == 'SinglePage':
        teamslot1, teamslot2, teamslot3 = st.columns(3, gap='large')

        with st.container():
            with teamslot1:
                st.header("Teamslot 1")
                state_key_pkmn = 'pkmn'
                add_p_row(state_key_pkmn)
                pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][0])
                pkmn_collection.append(pokerow_data)
            with teamslot2:
                st.header("Teamslot 2")
                # Select Pokemon
                add_p_row(state_key_pkmn)
                pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][1])
                pkmn_collection.append(pokerow_data)
            with teamslot3:
                st.header("Teamslot 3")
                # Select Pokemon
                add_p_row(state_key_pkmn)
                pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][2])
                pkmn_collection.append(pokerow_data)

        teamslot4, teamslot5, teamslot6 = st.columns(3)

        with st.container():
            with teamslot4:
                st.header("Teamslot 4")
                # Select Pokemon
                add_p_row(state_key_pkmn)
                pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][3])
                pkmn_collection.append(pokerow_data)
            with teamslot5:
                st.header("Teamslot 5")
                # Select Pokemon
                add_p_row(state_key_pkmn)
                pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][4])
                pkmn_collection.append(pokerow_data)
            with teamslot6:
                st.header("Teamslot 6")
                # Select Pokemon
                add_p_row(state_key_pkmn)
                pokerow_data, poke_data = generate_p_row(pkmn_list, st.session_state['pkmn'][5])
                pkmn_collection.append(pokerow_data)
    else:
        return


view_mode = {'SinglePage': single_page(choice), 'Tabbed': tabbed(choice)}

# ~~~~~ Code Graveyard ~~~~~~

# Select Pokemon
# poke_col1, poke_col2 = st.columns([.65, .75])
# Go Beavs!!!
# with poke_col1:
#     pkmn_selection = st.selectbox("Select a Pokemon", pkmn_list, key='pkmn1')
#     poke_data = pokemon_data_fetcher(pkmn_selection)
#     st.image(poke_data[0])
#     st.text("Type:")
#     for item in poke_data[3]:
#         image = Image.open(f'./functional_data/icons/{item}.png')
#         new_image = image.resize((100, 20))
#         st.image(new_image)
# with poke_col2:
#     # display dex entry
#     st.image(f'./functional_data/icons/pokedex.png')
#     st.write(poke_data[1])
#     st.slider('Level', min_value=1, max_value=100, step=1)


# Select moves
# move_dict = move_list(poke_data[2])
# pkmn_moves = move_dict.keys()
# pk1mv1_sel = st.selectbox("Select Move 1", pkmn_moves, key='pk1mv1')
# pk1mv1_data = move_data_fetcher(move_dict[pk1mv1_sel])
# with st.expander("Move Information"):
#     mv_col1, mv_col2 = st.columns([0.8, .75*4])
#     with mv_col1:
#         st.text("Type:")
#         st.image(f'./functional_data/icons/{pk1mv1_data[1]}.png')
#         st.text(f'Pow: {pk1mv1_data[2]}')
#         st.text(f'Acc: {pk1mv1_data[3]}')
#     with mv_col2:
#         st.write(pk1mv1_data[0])
