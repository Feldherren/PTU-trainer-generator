# possibly not necessary to track what evolutions a pokemon has
# actually, necessary to say we want something of a particular family

import configparser #https://docs.python.org/3/library/configparser.html
import argparse #https://docs.python.org/3/library/argparse.html

parser = argparse.ArgumentParser(description='Currently just filters for pokemon based on a supplied filter string')
parser.add_argument('filterstring', help='string to filter pokemon by')

args = parser.parse_args()

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

# filterString example: 'type=Grass;type=Poison'
def getFilteredPokemonList(filterString=None):
	filteredList = []
	for pokemon in pokemonData:
		#print(pokemon)
		filteredList.append(pokemon)
	
	if filterString is not None:
		for f in filterString.split(';'):
			filter = f.split('=')
			print("Filtering for:",filter[0],'=',filter[1])
			if filter[0].lower() == 'type':
				filteredList = filterPokemonList(list=filteredList,type=filter[1])
			elif filter[0].lower() == 'level':
				filteredList = filterPokemonList(list=filteredList,level=int(filter[1]))
			elif filter[0].lower() == 'diet':
				filteredList = filterPokemonList(list=filteredList,diet=filter[1])
			elif filter[0].lower() == 'habitat':
				filteredList = filterPokemonList(list=filteredList,habitat=filter[1])
			elif filter[0].lower() == 'eggGroup':
				filteredList = filterPokemonList(list=filteredList,eggGroup=filter[1])
			elif filter[0].lower() == 'family':
				filteredList = filterPokemonList(list=filteredList,family=filter[1])
			elif filter[0].lower() == 'ability':
				filteredList = filterPokemonList(list=filteredList,ability=filter[1])
			elif filter[0].lower() == 'basicability':
				filteredList = filterPokemonList(list=filteredList,basicAbility=filter[1])
			elif filter[0].lower() == 'advancedability':
				filteredList = filterPokemonList(list=filteredList,advancedAbility=filter[1])
			elif filter[0].lower() == 'highability':
				filteredList = filterPokemonList(list=filteredList,highAbility=filter[1])
	
	return filteredList

# just returns a list of pokemon names; these can be used with pokemonData to get actual data
# returns a list; the result can be run through set() to remove duplicates
# by default returns any pokemon that matches any filter condition. Can be set to return only pokemon that match all filter conditions.
def filterPokemonList(filterType='OR', list=None, type=None, level=None, diet=None, habitat=None, eggGroup=None, family=None, ability=None, basicAbility=None, advancedAbility=None, highAbility=None):
	if list == None:
		filteredList = []
		# populate with everything, then remove as necessary
		#print(filteredList)
		for pokemon in pokemonData:
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
		pTypes = None
		pMinimumLevel = None
		pDiets = None
		pHabitats = None
		pEggGroups = None
		pFamily = None
		pBasicAbilities = None
		pAdvancedAbilities = None
		pHighAbility = None
		
		if 'types' in pokemonData[pName]:
			pTypes = pokemonData[pName]['types'].split(',')
		if 'minimum_level' in pokemonData[pName]:
			pMinimumLevel = int(pokemonData[pName]['minimum_level'])
		if 'diets' in pokemonData[pName]:
			pDiets = pokemonData[pName]['diets'].split(',')
		if 'habitats' in pokemonData[pName]:
			pHabitats = pokemonData[pName]['habitats'].split(',')
		if 'egg_groups' in pokemonData[pName]:
			pEggGroups = pokemonData[pName]['egg_groups'].split(',')
		if 'family' in pokemonData[pName]:
			pFamily = pokemonData[pName]['family'].split(',')
		if 'basic_abilities' in pokemonData[pName]:
			pBasicAbilities = pokemonData[pName]['basic_abilities'].split(',')
		if 'advanced_abilities' in pokemonData[pName]:
			pAdvancedAbilities = pokemonData[pName]['advanced_abilities'].split(',')
		if 'high_ability' in pokemonData[pName]:
			pHighAbility = pokemonData[pName]['high_ability'].split(',')
		if 'capabilities' in pokemonData[pName]:
			pCapabilities = pokemonData[pName]['capabilities'].split(',')
		
		# it's getting information properly for the pokemon it checks, but for some reason it isn't checking all pokemon on the list, and randomly chooses what to check
		#print(pName, pType1, pType2, pMinimumLevel, pDiets, pHabitats, pEggGroups, pFamily)
		
		# now filter
		# TO-DO: when using 'AND' filtering, will only match pure types; looking for Grass, 'Grass/Poison' will be discarded because of 'Poison'
		if filterType == 'AND':
			removePokemon = False
			# if anything DOES NOT match, set removePokemon to True
			if type is not None:
				if pTypes is not None:
					#print(type,':',pTypes)
					if type not in pTypes:
						removePokemon = True
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
			if family is not None:
				if pFamily is not None:
					#print(family,':',pFamily)
					if family not in pFamily:
						removePokemon = True
			if ability is not None:
				if pBasicAbilities is not None:
					if ability not in pBasicAbilities:
						if pAdvancedAbilities is not None:
							if ability not in pAdvancedAbilities:
								if pHighAbility is not None:
									if ability not in pHighAbility:
										removePokemon = True
			if basicAbility is not None:
				if pBasicAbilities is not None:
					if basicAbility not in pBasicAbilities:
						removePokemon = True
			if advancedAbility is not None:
				if pAdvancedAbilities is not None:
					if advancedAbility not in pAdvancedAbilities:
						removePokemon = True
			if highAbility is not None:
				if pHighAbility is not None:
					if highAbility not in pHighAbility:
						removePokemon = True
		elif filterType == 'OR':
			removePokemon = True
			# if anything DOES match, set removePokemon to False
			if type is not None:
				if pTypes is not None:
					#print(type,':',pTypes)
					if type in pTypes:
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
			if family is not None:
				if pFamily is not None:
					#print(family,':',pFamily)
					if family in pFamily:
						removePokemon = False
			if ability is not None:
				if pBasicAbilities is not None:
					if ability in pBasicAbilities:
						removePokemon = False
				if pAdvancedAbilities is not None:
					if ability in pAdvancedAbilities:
						removePokemon = False
				if pHighAbility is not None:
					if ability in pHighAbility:
						removePokemon = False
			if basicAbility is not None:
				if pBasicAbilities is not None:
					if basicAbility in pBasicAbilities:
						removePokemon = False
			if advancedAbility is not None:
				if pAdvancedAbilities is not None:
					if advancedAbility in pAdvancedAbilities:
						removePokemon = False
			if highAbility is not None:
				if pHighAbility is not None:
					if highAbility in pHighAbility:
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

#print(set(filterPokemonList(pokemonData, type="Water")))
print(getFilteredPokemonList(args.filterstring))