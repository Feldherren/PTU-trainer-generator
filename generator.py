# possibly not necessary to track what evolutions a pokemon has
# actually, necessary to say we want something of a particular family

import configparser #https://docs.python.org/3/library/configparser.html

pokemonData = dict()

def loadData():
	# load data from ini files here
	pokemonConfig = configparser.ConfigParser()
	pokemonConfig.read('pokemon.ini')
	for pokemon in pokemonConfig:
		#print(pokemon)
		tempPokemon = dict()
		for value in pokemonConfig[pokemon]:
			#print(pokemonConfig[pokemon][value])
			tempPokemon[value] = pokemonConfig[pokemon][value]
		pokemonData[pokemon] = tempPokemon

def getRandomPokemon(type=None, level=None):
	# if no type or level supplied, assume 'any' for each
	# alternatively, match pokemon to trainer level if level is not specified?
	pokemon = None
	return pokemon

# just returns a list of pokemon names; these can be used with pokemonData to get actual data
# returns a list; the result can be run through set() to remove duplicates
# currently returns any pokemon that matches any value, rather than only pokemon that match the given value; EG. type="Grass", diet="Herbivore" currently returns Charmander, because Charmander is a herbivore, despite not being Grass
def getFilteredPokemonList(d, type=None, level=None, diet=None, habitat=None, egg_group=None):
	filteredList = []
	for pokemon in d:
		if type is not None:
			if 'type_1' in d[pokemon]:
				if d[pokemon]['type_1'] == type:
					filteredList.append(pokemon)
				elif 'type_2' in d[pokemon]:
					if d[pokemon]['type_2'] == type:
						filteredList.append(pokemon)
		if level is not None:
			if 'minimum_level' in d[pokemon]:
				if int(d[pokemon]['minimum_level']) <= level:
					filteredList.append(pokemon)
		if diet is not None:
			if 'diets' in d[pokemon]:
				if diet in d[pokemon]['diets'].split(','):
					filteredList.append(pokemon)
		if habitat is not None:
			if 'habitats' in d[pokemon]:
				if habitat in d[pokemon]['habitats'].split(','):
					filteredList.append(pokemon)
		if egg_group is not None:
			if 'egg_groups' in d[pokemon]:
				if egg_group in d[pokemon]['egg_groups'].split(','):
					filteredList.append(pokemon)
	return filteredList

loadData()

#print(pokemonData)

print(set(getFilteredPokemonList(pokemonData, habitat="Urban")))