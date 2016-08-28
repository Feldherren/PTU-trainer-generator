# possibly not necessary to track what evolutions a pokemon has
# actually, necessary to say we want something of a particular family
# To-DO: compatibility check, re: egg groups?

import configparser #https://docs.python.org/3/library/configparser.html
import argparse #https://docs.python.org/3/library/argparse.html

parser = argparse.ArgumentParser(description='Currently just filters for pokemon based on a supplied filter string')
#parser.add_argument('filterstring', help='string to filter pokemon by')

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
	# the above should probably be handled when calling this, not within the function
	pokemon = None
	return pokemon

def checkCompatibility(a, b):
	matches = list()
	if 'Indeterminate' not in getPokemonEggGroups(a) and 'Indeterminate' not in getPokemonEggGroups(b):
		if 'Ditto' in getPokemonEggGroups(a) or 'Ditto' in getPokemonEggGroups(b):
			return 'Ditto'
		else:
			for eggGroup in getPokemonEggGroups(a):
				if eggGroup in getPokemonEggGroups(b):
					matches.append(eggGroup)
					return matches

def printPokemonData(pName):
	#pokemonData[pName]
	print(pName,'(p'+pokemonData[pName]['page']+')')

def getPokemonTypes(pName):
	types = None
	if 'types' in pokemonData[pName]:
		types = [x.lower().strip() for x in pokemonData[pName]['types'].split(',')]
	return types

def getPokemonMinimumLevel(pName):
	minLevel = None
	if 'minimum_level' in pokemonData[pName]:
		minLevel = int(pokemonData[pName]['minimum_level'])
	return minLevel

def getPokemonDiets(pName):
	diets = None
	if 'diets' in pokemonData[pName]:
		diets = [x.lower().strip() for x in pokemonData[pName]['diets'].split(',')]
	return diets

def getPokemonHabitats(pName):
	habitats = None
	if 'habitats' in pokemonData[pName]:
		habitats = [x.lower().strip() for x in pokemonData[pName]['habitats'].split(',')]
	return habitats

def getPokemonEggGroups(pName):
	eggGroups = None
	if 'egg_groups' in pokemonData[pName]:
		eggGroups = [x.lower().strip() for x in pokemonData[pName]['egg_groups'].split(',')]
	return eggGroups

def getPokemonFamily(pName):
	family = None
	if 'family' in pokemonData[pName]:
		family = [x.lower().strip() for x in pokemonData[pName]['family'].split(',')]
	return family

def getPokemonBasicAbilities(pName):
	basicAbilities = None
	if 'basic_abilities' in pokemonData[pName]:
		basicAbilities = [x.lower().strip() for x in pokemonData[pName]['basic_abilities'].split(',')]
	return basicAbilities

def getPokemonAdvancedAbilities(pName):
	advancedAbilities = None
	if 'advanced_abilities' in pokemonData[pName]:
		advancedAbilities = [x.lower().strip() for x in pokemonData[pName]['advanced_abilities'].split(',')]
	return advancedAbilities

def getPokemonHighAbility(pName):
	highAbility = None
	if 'high_ability' in pokemonData[pName]:
		highAbility = pokemonData[pName]['high_ability'].lower()
	return highAbility

def getPokemonCapabilities(pName):
	capabilities = None
	if 'capabilities' in pokemonData[pName]:
		capabilities = [x.lower().strip() for x in pokemonData[pName]['capabilities'].split(',')]
	return capabilities

def getPokemonHeightClass(pName):
	height = None
	if 'height_class' in pokemonData[pName]:
		height = pokemonData[pName]['height_class'].lower()
	return height

def getPokemonWeightClass(pName):
	weight = None
	if 'weight_class' in pokemonData[pName]:
		weight = pokemonData[pName]['weight_class'].lower()
	return weight

def getPokemonLevelMoves(pName):
	levelMoves = dict()
	if 'level_moves' in pokemonData[pName]:
		for move in pokemonData[pName]['level_moves'].split(','):
			m = move.split(':')
			levelMoves[m[1].strip().lower()] = m[0].strip()
	return levelMoves

def getPokemonHMMoves(pName):
	hmMoves = None
	if 'hm_moves' in pokemonData[pName]:
		hmMoves = [x.lower().strip() for x in pokemonData[pName]['hm_moves'].split(',')]
	return hmMoves

def getPokemonTMMoves(pName):
	tmMoves = None
	if 'tm_moves' in pokemonData[pName]:
		tmMoves = [x.lower().strip() for x in pokemonData[pName]['tm_moves'].split(',')]
	return tmMoves

def getPokemonEggMoves(pName):
	eggMoves = None
	if 'egg_moves' in pokemonData[pName]:
		eggMoves = [x.lower().strip() for x in pokemonData[pName]['egg_moves'].split(',')]
	return eggMoves

def getPokemonTutorMoves(pName):
	tutorMoves = None
	if 'tutor_moves' in pokemonData[pName]:
		tutorMoves = [x.lower().strip() for x in pokemonData[pName]['tutor_moves'].split(',')]
	return tutorMoves

# filterString example: 'type=Grass;type=Poison'
def getFilteredPokemonList(filterString=None):
	filteredList = []
	for pokemon in pokemonData:
		#print(pokemon)
		filteredList.append(pokemon)
	
	# does not fail gracefully if you enter something like '0' or that doesn't match the usual pattern
	# TO-DO: fix error when the user enters something that isn't a valid filter string
	# error seems to be due to the split() function not being able to split invalid strings
	# also, do we want diet=!Omnivore, or diet!=Omnivore ?
	if filterString is not None:
		#print(filterString)
		for f in filterString.split(';'):
			filter = f.split('=')
			print("Filtering for:",filter[0],'=',filter[1])
			fType='OR'
			if filter[1][:1] == '!':
				fType='NOT'
				filter[1] = filter[1][1:]
			if filter[0].lower() == 'name':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,name=filter[1])
			if filter[0].lower() == 'type':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,type=filter[1])
			elif filter[0].lower() == 'level':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,level=int(filter[1]))
			elif filter[0].lower() == 'diet':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,diet=filter[1])
			elif filter[0].lower() == 'habitat':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,habitat=filter[1])
			elif filter[0].lower() == 'egggroup':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,eggGroup=filter[1])
			elif filter[0].lower() == 'family':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,family=filter[1])
			elif filter[0].lower() == 'ability':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,ability=filter[1])
			elif filter[0].lower() == 'basicability':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,basicAbility=filter[1])
			elif filter[0].lower() == 'advancedability':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,advancedAbility=filter[1])
			elif filter[0].lower() == 'highability':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,highAbility=filter[1])
			elif filter[0].lower() == 'move':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,levelMove=filter[1],hmMove=filter[1],tmMove=filter[1],tutorMove=filter[1],eggMove=filter[1])
			elif filter[0].lower() == 'levelmove':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,levelMove=filter[1])
			elif filter[0].lower() == 'hm' or filter[0].lower() == 'hmmove':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,hmMove=filter[1])
			elif filter[0].lower() == 'tm' or filter[0].lower() == 'tmmove':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,tmMove=filter[1])
			elif filter[0].lower() == 'tutor' or filter[0].lower() == 'tutormove':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,tutorMove=filter[1])
			elif filter[0].lower() == 'egg' or filter[0].lower() == 'eggmove':
				filteredList = filterPokemonList(filterType=fType,list=filteredList,eggMove=filter[1])
	
	return filteredList

# just returns a list of pokemon names; these can be used with pokemonData to get actual data
# by default returns any pokemon that matches any filter condition. Can be set to return only pokemon that do not match filter conditions
# TO-DO: make move searches return natural moves, such as 'High Jump Kick (N)' when searching for regular form of move ('High Jump Kick')
def filterPokemonList(filterType='OR', list=None, name=None, type=None, level=None, diet=None, habitat=None, eggGroup=None, family=None, ability=None, basicAbility=None, advancedAbility=None, highAbility=None, levelMove=None, hmMove=None, tmMove=None, eggMove=None, tutorMove=None):
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
		# get data for the pokemon
		pTypes = getPokemonTypes(pName)
		pMinimumLevel = getPokemonMinimumLevel(pName)
		pDiets = getPokemonDiets(pName)
		pHabitats = getPokemonHabitats(pName)
		pEggGroups = getPokemonEggGroups(pName)
		pFamily = getPokemonFamily(pName)
		pBasicAbilities = getPokemonBasicAbilities(pName)
		pAdvancedAbilities = getPokemonAdvancedAbilities(pName)
		pHighAbility = getPokemonHighAbility(pName)
		pCapabilities = getPokemonCapabilities(pName)
		pLevelMoves = getPokemonLevelMoves(pName)
		pHMMoves = getPokemonHMMoves(pName)
		pTMMoves = getPokemonTMMoves(pName)
		pEggMoves = getPokemonEggMoves(pName)
		pTutorMoves = getPokemonTutorMoves(pName)
		
		# now filter
		if filterType == 'NOT':
			removePokemon = False
			# if anything DOES match, set removePokemon to True
			if name is not None:
				if name.lower() in pName.lower():
				#if name in pName:
					removePokemon = True
			if type is not None:
				if pTypes is not None:
					#print(type,':',pTypes)
					if type.lower() in pTypes:
						removePokemon = True
			if level is not None:
				if pMinimumLevel is not None:
					#print(level,':',pMinimumLevel)
					if pMinimumLevel <= level:
						removePokemon = True
			if diet is not None:
				if pDiets is not None:
					#print(diet,':',pDiets)
					if diet.lower() in pDiets:
						removePokemon = True
			if habitat is not None:
				if pHabitats is not None:
					#print(habitat,':',pHabitats)
					if habitat.lower() in pHabitats:
						removePokemon = True
			if eggGroup is not None:
				if pEggGroups is not None:
					#print(eggGroup,':',pEggGroups)
					if eggGroup.lower() in pEggGroups:
						removePokemon = True
			if family is not None:
				if pFamily is not None:
					#print(family,':',pFamily)
					if family.lower() in pFamily:
						removePokemon = True
			if ability is not None:
				if pBasicAbilities is not None:
					if ability.lower() in pBasicAbilities:
						removePokemon = True
				if pAdvancedAbilities is not None:
					if ability.lower() in pAdvancedAbilities:
						removePokemon = True
				if pHighAbility is not None:
					if ability.lower() in pHighAbility:
						removePokemon = True
			if basicAbility is not None:
				if pBasicAbilities is not None:
					if basicAbility.lower() in pBasicAbilities:
						removePokemon = True
			if advancedAbility is not None:
				if pAdvancedAbilities is not None:
					if advancedAbility.lower() in pAdvancedAbilities:
						removePokemon = True
			if highAbility is not None:
				if pHighAbility is not None:
					if highAbility.lower() in pHighAbility:
						removePokemon = True
			if levelMove is not None:
				if pLevelMoves is not None:
					if levelMove.lower() in pLevelMoves:
						removePokemon = True
			if hmMove is not None:
				if pHMMoves is not None:
					if hmMove.lower() in pHMMoves:
						removePokemon = True
			if tmMove is not None:
				if pTMMoves is not None:
					if tmMove.lower() in pTMMoves:
						removePokemon = True
			if eggMove is not None:
				if pEggMoves is not None:
					if eggMove.lower() in pEggMoves:
						removePokemon = True
			if tutorMove is not None:
				if pTutorMoves is not None:
					if tutorMove.lower() in pTutorMoves:
						removePokemon = True
		elif filterType == 'OR':
			removePokemon = True
			# if anything DOES match, set removePokemon to False
			if name is not None:
				if name.lower() in pName.lower():
				#if name in pName:
					removePokemon = False
			if type is not None:
				if pTypes is not None:
					#print(type,':',pTypes)
					if type.lower() in pTypes:
						removePokemon = False
			if level is not None:
				if pMinimumLevel is not None:
					#print(level,':',pMinimumLevel)
					if pMinimumLevel <= level:
						removePokemon = False
			if diet is not None:
				if pDiets is not None:
					#print(diet,':',pDiets)
					if diet.lower() in pDiets:
						removePokemon = False
			if habitat is not None:
				if pHabitats is not None:
					#print(habitat,':',pHabitats)
					if habitat.lower() in pHabitats:
						removePokemon = False
			if eggGroup is not None:
				if pEggGroups is not None:
					#print(eggGroup,':',pEggGroups)
					if eggGroup.lower() in pEggGroups:
						removePokemon = False
			if family is not None:
				if pFamily is not None:
					#print(family,':',pFamily)
					if family.lower() in pFamily:
						removePokemon = False
			if ability is not None:
				if pBasicAbilities is not None:
					if ability.lower() in pBasicAbilities:
						removePokemon = False
				if pAdvancedAbilities is not None:
					if ability.lower() in pAdvancedAbilities:
						removePokemon = False
				if pHighAbility is not None:
					if ability.lower() in pHighAbility:
						removePokemon = False
			if basicAbility is not None:
				if pBasicAbilities is not None:
					if basicAbility.lower() in pBasicAbilities:
						removePokemon = False
			if advancedAbility is not None:
				if pAdvancedAbilities is not None:
					if advancedAbility.lower() in pAdvancedAbilities:
						removePokemon = False
			if highAbility is not None:
				if pHighAbility is not None:
					if highAbility.lower() in pHighAbility:
						removePokemon = False
			if levelMove is not None:
				if pLevelMoves is not None:
					if levelMove.lower() in pLevelMoves:
						removePokemon = False
			if hmMove is not None:
				if pHMMoves is not None:
					if hmMove.lower() in pHMMoves:
						removePokemon = False
			if tmMove is not None:
				if pTMMoves is not None:
					if tmMove.lower() in pTMMoves:
						removePokemon = False
			if eggMove is not None:
				if pEggMoves is not None:
					if eggMove.lower() in pEggMoves:
						removePokemon = False
			if tutorMove is not None:
				if pTutorMoves is not None:
					if tutorMove.lower() in pTutorMoves:
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

#print(getFilteredPokemonList('type=Water')))
#print(getFilteredPokemonList(args.filterstring))

mainMenu = "-1"

while True:
	if mainMenu == "-1":
		print("1. Pokedex")
		print("0. Quit")
		mainMenu = input("> ")
	elif mainMenu == "0":
		quit()
	elif mainMenu == "1":
		print("1. Search")
		print("2. Pokemon Information")
		print("3. Check Compatibility")
		print("R. Reload Data")
		print("0. Back")
		pokedexMenu = input("> ")
		if pokedexMenu == "0": # Back
			mainMenu = "-1"
		elif pokedexMenu == "1": # Search
			print("Enter filter string. Format: key=value to search for pokemon with a particular value,key=!value to search for pokemon without that value, semi-colon to separate filter criteria.")
			searchString = input("> ")
			for p in getFilteredPokemonList(searchString):
				print(p)
		elif pokedexMenu == "2": # Pokemon Information
			pName = input("Pokemon name> ")
			printPokemonData(pName)
		elif pokedexMenu == "3": # Check Compatibility
			compatibility = None
			pokemonA = input("Pokemon A> ")
			pokemonB = input("Pokemon B> ")
			compatibility = checkCompatibility(pokemonA, pokemonB)
			if compatibility is not None:
				print(pokemonA,'+',pokemonB + ': Compatible (' + str(compatibility) + ')')
			else:
				print(pokemonA,'+',pokemonB + ': Incompatible')
		elif pokedexMenu == "R": # Reload Data
			loadData()