# possibly not necessary to track what evolutions a pokemon has
# actually, necessary to say we want something of a particular family?

# TO-DO: get type data directly from config, instead of loading it into a dict
# TO-DO: get pokemon data directly from config, instead of loading it into a dict
# TO=DO: searching for legendary/fossil pokemon is a kludge, should be fixed somehow
#	EG. currently getFilteredPokemonList takes 'legendary=False' in string, goes 'fType='NOT',legendary=True' to filterPokemonList regardless; instead filterPokemonList should only care about True/False/None
#	Probably need to overhaul filterPokemonList entirely, as the fType thing is annoying to work with
# in these cases, not just a matter of changing typeData to typeConfig everywhere

import configparser #https://docs.python.org/3/library/configparser.html
import argparse #https://docs.python.org/3/library/argparse.html
import random #https://docs.python.org/3.5/library/random.html

parser = argparse.ArgumentParser(description='Currently just filters for pokemon based on a supplied filter string')
#parser.add_argument('filterstring', help='string to filter pokemon by')

args = parser.parse_args()

pokemonData = dict()
typeData = dict()
natureData = dict()
# pokemonConfig = configparser.ConfigParser()
# pokemonConfig.read('pokemon.ini')
# typeConfig = configparser.ConfigParser()
# typeConfig.read('types.ini')
# the above doesn't work by itself
natureConfig = configparser.ConfigParser()
natureConfig.read('natures.ini')

def loadData():
	# load data from ini files here
	# load pokemon data
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
	# load type data
	typeConfig = configparser.ConfigParser()
	typeConfig.read('types.ini')
	for type in typeConfig:
		if type is not 'DEFAULT':
			tempType = dict()
			for value in typeConfig[type]:
				tempType[value] = [x.lower().strip() for x in typeConfig[type][value].split(',')]
			typeData[type.lower()] = tempType

# set legendaryPokemon and fossilPokemon to None for no-preference
def generateRandomTrainer(team=False, legendaryPokemon=False, fossilPokemon=False, minLevel=1, maxLevel=50, gender=None, noPokemon=None):
	trainer = dict()
	# generate trainer details
	# set level
	trainer['level'] = random.choice(range(minLevel, maxLevel))
	# set gender
	if gender is not None:
		trainer['gender'] = gender
	else:
		trainer['gender'] = random.choice(('male', 'female'))
	# combat stats
	statPoints = 10
	combatStats = {'hp':10, 'attack':5, 'defense':5, 'specialAttack':5, 'specialDefense':5, 'speed':5}
	eligibleStats = ['hp', 'attack', 'defense', 'specialAttack', 'specialDefense', 'speed']
	for i in range(statPoints):
		randomStat = random.choice(eligibleStats)
		combatStats[randomStat] = combatStats[randomStat]+1
		if randomStat == 'hp':
			if combatStats[randomStat] >= 15:
				eligibleStats.remove(randomStat)
		else:
			if combatStats[randomStat] >= 10:
				eligibleStats.remove(randomStat)
	trainer['combatStats'] = combatStats
	# generate pokemon team
	# currently just adds names to a list, with no filtering, but should at least filter based on trainer classes
	# later, generate pokemon instead of getting a random pokemon species?
	pTeam = []
	if noPokemon is None:
		# just equal distribution of team size, here
		# a distribution more biased towards the middle would be (1,2,2,3,3,3,4,4,4,5,5,6,6)
		noPokemon = random.choice((1,2,3,4,5,6))
	for i in range(noPokemon):
		pTeam.append(getRandomPokemon(legendary=legendaryPokemon, fossil=fossilPokemon))
	trainer['pokemon'] = pTeam
	return trainer

# legendary and fossil: False, True or None? False disallows it, True means it must be, and None means it can be?
def generatePokemon(shiny=False, species=None, nature=None, minLevel=1, maxLevel=100):
	pokemon = dict()
	# set level
	# level should probably affect evolution tier? Currently getting a lot of level 97 Fletchlings or similar
	pokemon['level'] = random.choice(range(minLevel, maxLevel))
	# set species
	# if we want filtered species generation, do that before using this function and supply the result to this
	if species is None:
		species = getRandomPokemon(level=pokemon['level'])
	pokemon['species'] = species
	# set combat stats
	combatStats = getPokemonBaseStats(species)
	pokemon['combatStats'] = combatStats
	# set nature
	if nature is not None:
		pokemon['nature'] = nature
	else:
		pokemon['nature'] = random.choice(natureConfig.sections())
	# change base stats due to nature
	if natureConfig[pokemon['nature']]['raises'] == 'hp':
		pokemon['combatStats'][natureConfig[pokemon['nature']]['raises']] = pokemon['combatStats'][natureConfig[pokemon['nature']]['raises']] + 1
	else:
		pokemon['combatStats'][natureConfig[pokemon['nature']]['raises']] = pokemon['combatStats'][natureConfig[pokemon['nature']]['raises']] + 2
	if natureConfig[pokemon['nature']]['lowers'] == 'hp':
		pokemon['combatStats'][natureConfig[pokemon['nature']]['lowers']] = pokemon['combatStats'][natureConfig[pokemon['nature']]['lowers']] - 1
	else:
		pokemon['combatStats'][natureConfig[pokemon['nature']]['lowers']] = pokemon['combatStats'][natureConfig[pokemon['nature']]['lowers']] - 2
		
	# check if shiny
	shinyRoll = random.choice(range(1,100))
	if shinyRoll == 100:
		shiny = True
	pokemon['shiny'] = shiny
	return pokemon

# legendary and fossil: False, True or None? False disallows it, True means it must be, and None means it can be?
def getRandomPokemon(type=None, level=None, legendary=None, fossil=None):
	# if no type or level supplied, assume 'any' for each
	# alternatively, match pokemon to trainer level if level is not specified?
	# the above should probably be handled when calling this, not within the function
	pokemon = None
	j = []
	if type is not None:
		typeString = 'type=' + type
		j.append(typeString)
	if level is not None:
		levelString = 'level=' + str(level)
		j.append(levelString)
	if legendary is not None:
		if legendary is False:
			legendaryString = 'legendary=False'
		elif legendary is True:
			legendaryString = 'legendary=True'
		j.append(legendaryString)
	if fossil is not None:
		if fossil is False:
			fossilString = 'fossil=False'
		elif fossil is True:
			fossilString = 'fossil=True'
		j.append(fossilString)
	searchString = ';'.join(j)
	l = getFilteredPokemonList(searchString)
	pokemon = random.choice(l)
	return pokemon

def checkTypeEffectiveness(attackingType, defendingType):
	effectiveness = 1
	#print("checkTypeEffectiveness:", attackingType, defendingType)
	#print(typeData[attackingType]['super_effective'])
	if 'super_effective' in typeData[attackingType]:
		if defendingType in typeData[attackingType]['super_effective']:
			#print("checkTypeEffectiveness:", attackingType, "attacking", defendingType, "= super effective!")
			effectiveness = 2
		elif 'resistant' in typeData[attackingType]:
			if defendingType in typeData[attackingType]['resistant']:
				#print("checkTypeEffectiveness:", attackingType, "attacking", defendingType, "= resistant!")
				effectiveness = 0.5
			else:
				if 'immune' in typeData[attackingType]:
					if defendingType in typeData[attackingType]['immune']:
						effectiveness = 0
						#print("checkTypeEffectiveness:", attackingType, "attacking", defendingType, "= immune!")
	#print(effectiveness)
	return effectiveness

def checkAttackEffectiveness(pokemon, attackType):
	effectiveness = 1
	for type in getPokemonTypes(pokemon):
		effectiveness = effectiveness * checkTypeEffectiveness(attackType.lower(), type)
	return effectiveness

def checkDefensiveEffectiveness(pokemon):
	defense = dict()
	for attackType in typeData:
		effectiveness = checkAttackEffectiveness(pokemon, attackType)
		if effectiveness in defense:
			defense[effectiveness].append(attackType)
		else:
			defense[effectiveness] = [attackType]
	return defense

def printDefensiveEffectiveness(defense):
	order = []
	for e in defense:
		order.append(e)
	order.sort(reverse=True)
	for effectiveness in order:
		print('X' + str(effectiveness) + ': ' + ', '.join(defense[effectiveness]))

# checks the breeding compatibility between two pokemon of named species
# returns the first matching egg group found, or nothing
def checkCompatibility(a, b):
	if 'Indeterminate' not in getPokemonEggGroups(a) and 'Indeterminate' not in getPokemonEggGroups(b):
		if 'ditto' in getPokemonEggGroups(a) or 'ditto' in getPokemonEggGroups(b):
			return 'ditto'
		else:
			for eggGroup in getPokemonEggGroups(a):
				if eggGroup in getPokemonEggGroups(b):
					return eggGroup

def printPokemonData(pName):
	#pokemonData[pName]
	print(pName,'(p'+pokemonData[pName]['page']+')')

def getPokemonBaseStats(pName):
	baseStats = dict()
	baseStats['hp'] = int(pokemonData[pName]['base_hp'])
	baseStats['attack'] = int(pokemonData[pName]['base_attack'])
	baseStats['defense'] = int(pokemonData[pName]['base_defense'])
	baseStats['special_attack'] = int(pokemonData[pName]['base_special_attack'])
	baseStats['special_defense'] = int(pokemonData[pName]['base_special_defense'])
	baseStats['speed'] = int(pokemonData[pName]['base_speed'])
	return baseStats
	
def getPokemonTypes(pName):
	types = None
	if 'types' in pokemonData[pName]:
		types = [x.lower().strip() for x in pokemonData[pName]['types'].split(',')]
	#print(types)
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

def isLegendary(pName):
	legendary = False
	if 'legendary' in pokemonData[pName]:
		if pokemonData[pName]['legendary'] == 'True':
			legendary = True
	return legendary

def isFossil(pName):
	fossil = False
	if 'fossil' in pokemonData[pName]:
		if pokemonData[pName]['fossil'] == 'True':
			fossil = True
	return fossil

# filterString example: 'type=Grass;type=Poison'
# change this to also optionally take variables like filterPokemonList?
# write a function that interprets the filterstring for this?
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
			if filter[0] is not '':
				#print("Filtering for:",filter[0],'=',filter[1])
				fType='OR'
				if filter[1] is not None:
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
					filteredList = filterPokemonList(filterType=fType,list=filteredList,basicAbility=filter[1],advancedAbility=filter[1],highAbility=filter[1])
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
				elif filter[0].lower() == 'legendary':
					if filter[1] == 'True':
						filteredList = filterPokemonList(list=filteredList,legendary=True)
					if filter[1] == 'False':
						filteredList = filterPokemonList(filterType='NOT',list=filteredList,legendary=True)
				elif filter[0].lower() == 'fossil':
					if filter[1] == 'True':
						filteredList = filterPokemonList(list=filteredList,fossil=True)
					if filter[1] == 'False':
						filteredList = filterPokemonList(filterType='NOT',list=filteredList,fossil=True)
	
	return filteredList

# just returns a list of pokemon names; these can be used with pokemonData to get actual data
# by default returns any pokemon that matches any filter condition. Can be set to return only pokemon that do not match filter conditions
# TO-DO: make move searches return natural moves, such as 'High Jump Kick (N)' when searching for regular form of move ('High Jump Kick')
def filterPokemonList(filterType='OR', list=None, name=None, type=None, level=None, diet=None, habitat=None, eggGroup=None, family=None, ability=None, basicAbility=None, advancedAbility=None, highAbility=None, levelMove=None, hmMove=None, tmMove=None, eggMove=None, tutorMove=None, legendary=None, fossil=None):
	if list == None:
		filteredList = []
		# populate with everything, then remove as necessary
		#print(filteredList)
		for pokemon in pokemonData:
			#print(pokemon)
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
		pFossil = isFossil(pName)
		pLegendary = isLegendary(pName)
		#print(pFossil)
		#print(pLegendary)
		
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
					elif 'any' in pHMMoves:
						removePokemon = True
			if tmMove is not None:
				if pTMMoves is not None:
					if tmMove.lower() in pTMMoves:
						removePokemon = True
					elif 'any' in pTMMoves:
						removePokemon = True
			if eggMove is not None:
				if pEggMoves is not None:
					if eggMove.lower() in pEggMoves:
						removePokemon = True
			if tutorMove is not None:
				if pTutorMoves is not None:
					if tutorMove.lower() in pTutorMoves:
						removePokemon = True
					elif 'any' in pTutorMoves:
						removePokemon = True
			if legendary is not None:
				if pLegendary is True:
					if legendary == True:
						removePokemon = True
			if fossil is not None:
				if pFossil is True:
					if fossil == True:
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
					elif 'any' in pHMMoves:
						removePokemon = False
			if tmMove is not None:
				if pTMMoves is not None:
					if tmMove.lower() in pTMMoves:
						removePokemon = False
					elif 'any' in pTMMoves:
						removePokemon = False
			if eggMove is not None:
				if pEggMoves is not None:
					if eggMove.lower() in pEggMoves:
						removePokemon = False
			if tutorMove is not None:
				if pTutorMoves is not None:
					if tutorMove.lower() in pTutorMoves:
						removePokemon = False
					elif 'any' in pEggMoves:
						removePokemon = False
			if legendary is not None:
				if pLegendary is True:
					if legendary == False:
						removePokemon = True
					elif legendary is not None:
						removePokemon = False
			if fossil is not None:
				if pFossil is True:
					if fossil == False:
						removePokemon = True
					elif fossil is not None:
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
		print("2. Random Generation")
		print("0. Quit")
		mainMenu = input("> ")
	elif mainMenu == "0":
		quit()
	elif mainMenu == "1":
		print("1. Search")
		print("2. Pokemon Information")
		print("3. Check Breeding Compatibility")
		print("4. Check Attack Effectiveness")
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
		elif pokedexMenu == "4": # Check Attack Effectiveness
			pName = input("Pokemon name> ")
			#aType = input("Attacking type> ")
			#print("Damage X" + str(checkAttackEffectiveness(pName, aType)))
			# instead, get all attack effectivenesses from this option
			printDefensiveEffectiveness(checkDefensiveEffectiveness(pName))
		elif pokedexMenu == "R": # Reload Data
			loadData()
		else:
			pokedexMenu = '-1'
	elif mainMenu == "2":
		generatorMenu = '-1'
		print("1. Random Trainer")
		print("2. Random Pokemon")
		print("0. Back")
		generatorMenu = input("> ")
		if generatorMenu == "0": # Back
			mainMenu = "-1"
		elif generatorMenu == "1": # Random Trainer
			print(generateRandomTrainer())
		elif generatorMenu == "2": # Random Pokemon
			print(generatePokemon())
	else:
		mainMenu = "-1"