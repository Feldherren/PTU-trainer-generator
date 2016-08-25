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
		# The 'DEFAULT' entry is getting added here, for some reason; a section with the name 'DEFAULT'? Despite it not existing?
		if pokemon is not 'DEFAULT':
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
# by default returns any pokemon that matches any filter condition. Can be set to return only pokemon that match all filter conditions.
def getFilteredPokemonList(d, filterType='OR', list=None, type=None, level=None, diet=None, habitat=None, eggGroup=None):
	if list == None:
		filteredList = []
		# populate with everything, then remove as necessary
		#print(filteredList)
		for pokemon in d:
			#print(pokemon)
			if pokemon is not 'DEFAULT':
				filteredList.append(pokemon)
	else:
		filteredList = list
	
	#print("Filter Type:", filterType)
	
	# now start filtering things from the list
	remDict = dict()
	for pName in filteredList:
		#print(pName)
		# get data for the pokemon
		pType1 = None
		pType2 = None
		pMinimumLevel = None
		pDiets = None
		pHabitats = None
		pEggGroups = None
		
		if 'type_1' in d[pName]:
			pType1 = d[pName]['type_1']
		if 'type_2' in d[pName]:
			pType2 = d[pName]['type_2']
		if 'minimum_level' in d[pName]:
			pMinimumLevel = d[pName]['minimum_level']
		if 'diets' in d[pName]:
			pDiets = d[pName]['diets'].split(',')
		if 'habitats' in d[pName]:
			pHabitats = d[pName]['habitats'].split(',')
		if 'egg_groups' in d[pName]:
			pEggGroups = d[pName]['egg_groups'].split(',')
		
		# it's getting information properly for the pokemon it checks, but for some reason it isn't checking all pokemon on the list, and randomly chooses what to check
		#print(pName, pType1, pType2, pMinimumLevel, pDiets, pHabitats, pEggGroups)
		
		# now filter
		# TO-DO: when using 'AND' filtering, will only match pure types; looking for Grass, 'Grass/Poison' will be discarded because of 'Poison'
		if filterType == 'AND':
			removePokemon = False
			# if anything DOES NOT match, set removePokemon to True
			if type is not None:
				if pType1 is not None:
					#print(type,':',pType1)
					if pType1 != type:
						removePokemon = True
						if pType2 is not None:
							#print(type,':',pType2)
							if pType2 == type:
								removePokemon = False
			if level is not None:
				if pMinimumLevel is not None:
					#print(level,':',pMinimumLevel)
					if pMinimumLevel > level:
						removePokemon = True
			if diet is not None:
				if pDiets is not None:
					#print(diet,':',pDiets)
					if diet not in pDiets:
						removePokemon = True
			if habitat is not None:
				if pHabitats is not None:
					#print(habitat,':',pHabitats)
					if habitat not in pHabitats:
						removePokemon = True
			if eggGroup is not None:
				if pEggGroups is not None:
					#print(eggGroup,':',pEggGroups)
					if eggGroup not in pEggGroups:
						removePokemon = True
		elif filterType == 'OR':
			removePokemon = True
			# if anything DOES match, set removePokemon to False
			if type is not None:
				if pType1 is not None:
					#print(type,':',pType1)
					if pType1 == type:
						removePokemon = False
				if pType2 is not None:
					#print(type,':',pType2)
					if pType2 == type:
						removePokemon = False
			if level is not None:
				if pMinimumLevel is not None:
					#print(level,':',pMinimumLevel)
					if pMinimumLevel <= level:
						removePokemon = False
			if diet is not None:
				if pDiets is not None:
					#print(diet,':',pDiets)
					if diet in pDiets:
						removePokemon = False
			if habitat is not None:
				if pHabitats is not None:
					#print(habitat,':',pHabitats)
					if habitat in pHabitats:
						removePokemon = False
			if eggGroup is not None:
				if pEggGroups is not None:
					#print(eggGroup,':',pEggGroups)
					if eggGroup in pEggGroups:
						removePokemon = False
		
		#print(pName,':',removePokemon)
		# we can't actually remove stuff here, as that would interfere with looping through the list
		if removePokemon:
			remDict[pName] = True
	
	for pName in remDict:
		filteredList.remove(pName)
	
	return filteredList

loadData()

#print(pokemonData)

#print(set(getFilteredPokemonList(pokemonData, type="Water")))
print(getFilteredPokemonList(pokemonData, filterType="AND", habitat="Grassland", type="Grass"))