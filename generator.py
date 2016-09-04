# possibly not necessary to track what evolutions a pokemon has
# actually, necessary to say we want something of a particular family?

# TO-DO: get type data directly from config, instead of loading it into a dict
# in these cases, not just a matter of changing typeData to typeConfig everywhere
# TO-DO: get pokemon data directly from config, instead of loading it into a dict
# TO-DO: searching for legendary/fossil pokemon is a kludge, should be fixed somehow
#	EG. currently getFilteredPokemonList takes 'legendary=False' in string, goes 'fType='NOT',legendary=True' to filterPokemonList regardless; instead filterPokemonList should only care about True/False/None
#	Probably need to overhaul filterPokemonList entirely, as the fType thing is annoying to work with

import configparser #https://docs.python.org/3/library/configparser.html
import argparse #https://docs.python.org/3/library/argparse.html
import random #https://docs.python.org/3.5/library/random.html
import operator # for getting baseStatRelation order

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
dataConfig = configparser.ConfigParser()
dataConfig.read('datafiles.ini')
natureConfig = configparser.ConfigParser()
natureConfig.read(dataConfig['DATA']['natures'])
movesConfig = configparser.ConfigParser()
movesConfig.read(dataConfig['DATA']['moves'])

def loadData():
	# load data from ini files here
	# load pokemon data
	pokemonConfig = configparser.ConfigParser()
	pokemonConfig.read(dataConfig['DATA']['pokedex'])
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
	typeConfig.read(dataConfig['DATA']['types'])
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
	combatStats = {'hp':10, 'attack':5, 'defense':5, 'special_attack':5, 'special_defense':5, 'speed':5}
	eligibleStats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
	for i in range(statPoints):
		randomStat = random.choice(eligibleStats)
		combatStats[randomStat] = combatStats[randomStat]+1
		if randomStat == 'hp':
			if combatStats[randomStat] >= 15:
				eligibleStats.remove(randomStat)
		else:
			if combatStats[randomStat] >= 10:
				eligibleStats.remove(randomStat)
	# now apply stat points from levels
	statPoints = trainer['level']
	eligibleStats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
	for i in range(statPoints):
		randomStat = random.choice(eligibleStats)
		combatStats[randomStat] = combatStats[randomStat]+1
	trainer['combatStats'] = combatStats
	# generate pokemon team
	# currently just adds names to a list, with no filtering, but should at least filter based on trainer classes
	# should this have a chance of generating untrained pokemon?
	pTeam = []
	if noPokemon is None:
		# just equal distribution of team size, here
		# a distribution more biased towards the middle would be (1,2,2,3,3,3,4,4,4,5,5,6,6)
		noPokemon = random.choice((1,2,3,4,5,6))
	for i in range(noPokemon):
		pTeam.append(generatePokemon(species=getRandomPokemon(legendary=legendaryPokemon, fossil=fossilPokemon), trained=True))
	trainer['pokemon'] = pTeam
	return trainer

def printTrainer(trainer):
	print('Level:', trainer['level'])
	print('Gender:', trainer['gender'])
	print('\nCombat Stats')
	print('HP:', trainer['combatStats']['hp'])
	print('Attack:', trainer['combatStats']['attack'])
	print('Defense:', trainer['combatStats']['defense'])
	print('Special Attack:', trainer['combatStats']['special_attack'])
	print('Special Defense:', trainer['combatStats']['special_defense'])
	print('Speed:', trainer['combatStats']['speed'])
	print('\nPokemon:')
	for pokemon in trainer['pokemon']:
		printPokemon(pokemon)

# legendary and fossil: False, True or None? False disallows it, True means it must be, and None means it can be?
def generatePokemon(shiny=False, species=None, nature=None, trained=False, minLevel=1, maxLevel=100):
	pokemon = dict()
	# set level
	# level should probably affect evolution tier? Currently getting a lot of level 97 Fletchlings or similar
	pokemon['level'] = random.choice(range(minLevel, maxLevel))
	# determine tutor point total; pokemon start with 1 and gain 1 every 5 levels
	pokemon['tutorPoints'] = int(int(pokemon['level'])/5)+1
	# set species
	# if we want filtered species generation, do that before using this function and supply the result to this
	if species is None:
		species = getRandomPokemon(level=pokemon['level'])
	pokemon['species'] = species
	if random.randrange(1000) <= float(pokemonData[pokemon['species']]['gender_ratio_m'])*10:
		pokemon['gender'] = 'Male'
	else:
		pokemon['gender'] = 'Female'
	# TO-DO: check evolutions here, scaling chance to evolve the thing based on how many levels from the minimum for an evolution?
	# how many levels until evolution-chance is 100%?
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
	# record pokemon baseStats for later (needed if nature is changed, for example)
	# though this shouldn't be needed for that since absolute base stats are stored in the pokedex data file, this might still be useful somewhere
	pokemon['baseStats'] = pokemon['combatStats']
	# calculate base stat relation
	pokemon['baseStatRelation'] = calculateBaseStatRelation(pokemon['combatStats'])
	#print(pokemon['baseStatRelation'])
	statPoints = 10 + pokemon['level']
	for i in range(statPoints):
		eligibleStats = getImprovableStats(pokemon['baseStatRelation'], pokemon['combatStats'])
		# check what's eligible or what will break base stat relation at this point, and remove it from the list of eligible stats?
		randomStat = random.choice(eligibleStats)
		combatStats[randomStat] = combatStats[randomStat]+1
	# determine what moves it has
	# get list of available moves; cull moves only available above its level, and tutor/tm/hm moves if not trained; only egg moves and tutor moves should be available to regular wild pokemon
	# TO-DO: currently only respects the current species; won't get moves from earlier evolutions, for example. So, simulate levelling up to the current level, from 1? At least, for wild species; trainers could have earlier moves tutored
	# not a big issue except for type-changing things (specifically Eevee), and things like Metapod or Kakuna that only learn Harden
	movesAvailable = []
	movesLearned = []
	levelMoves = getPokemonLevelMoves(pokemon['species'])
	if pokemon['species'] == 'Mew':
		for move in levelMoves:
			if int(levelMoves[move]) <= pokemon['level']:
				movesAvailable.append(move)
		if getPokemonEggMoves(pokemon['species']) is not None:
			for move in getPokemonEggMoves(pokemon['species']):
				movesAvailable.append(move)
		if trained:
			# get all moves from moves.ini, as they can all be tutored
			for move in movesConfig:
				movesAvailable.append(move)
	else:
		for move in levelMoves:
			if int(levelMoves[move]) <= pokemon['level']:
				movesAvailable.append(move)
		if getPokemonEggMoves(pokemon['species']) is not None:
			for move in getPokemonEggMoves(pokemon['species']):
				movesAvailable.append(move)
		if trained:
			# should this respect tutor points, eventually?
			# Problem is there are tutor things that cost 2TP and tutor things that cost 1TP, and can teach the same moves
			if getPokemonHMMoves(pokemon['species']) is not None:
				for move in getPokemonHMMoves(pokemon['species']):
					movesAvailable.append(move)
			if getPokemonTMMoves(pokemon['species']) is not None:
				for move in getPokemonTMMoves(pokemon['species']):
					movesAvailable.append(move)
			if getPokemonTutorMoves(pokemon['species']) is not None:
				for move in getPokemonTutorMoves(pokemon['species']):
					movesAvailable.append(move)
	# randomly choose moves and pop them from the list as they're picked, to avoid duplicates
	while len(movesAvailable) > 0 and len(movesLearned) < 6:
		move = random.choice(movesAvailable)
		movesLearned.append(move)
		for i in range(movesAvailable.count(move)):
			movesAvailable.pop(movesAvailable.index(move))
	pokemon['movesLearned'] = movesLearned
	# check if shiny
	shinyRoll = random.choice(range(1,100))
	if shinyRoll == 100:
		shiny = True
	pokemon['shiny'] = shiny
	# set name
	# check if trainer prefers nicknames, and give a nickname if so?
	pokemon['name'] = species
	return pokemon

def printPokemon(pokemon):
	print('Name:', pokemon['name'])
	print('Species:', pokemon['species'])
	print('Gender:', pokemon['gender'])
	print('Types:', pokemonData[pokemon['species']]['types'])
	print('Level:', pokemon['level'])
	print('\nCombat Stats')
	print('HP:', pokemon['combatStats']['hp'])
	print('Attack:', pokemon['combatStats']['attack'])
	print('Defense:', pokemon['combatStats']['defense'])
	print('Special Attack:', pokemon['combatStats']['special_attack'])
	print('Special Defense:', pokemon['combatStats']['special_defense'])
	print('Speed:', pokemon['combatStats']['speed'])
	print('\nMoves Known:')
	for move in pokemon['movesLearned']:
		print(move.title())

# calculates the base stat relation of the pokemon
# returns a dict of lists containing tiered stats, highest base value to lowest
# needs to be iterated through with a 'for i in range (len(baseStatRelation)):', I think, to keep it in order? with baseStatRelation[i-1] to get the tiers
# EG. 0 contains a list containing the highest stats, 1 would contain the tier below 0, 2 would contain the tier below 1, et cetera
def calculateBaseStatRelation(baseStats):
	tempStatOrder = sorted(baseStats.items(), key=operator.itemgetter(1), reverse=True)
	baseStatRelation = dict()
	lastValue = 0
	listIndex = -1
	for stat in tempStatOrder:
		#print(stat)
		if stat[1] != lastValue:
			listIndex = listIndex + 1
			lastValue = stat[1]
			baseStatRelation[listIndex] = [stat[0]]
		else:
			baseStatRelation[listIndex].append(stat[0])
			lastValue = stat[1]
	return baseStatRelation

def getImprovableStats(baseStatRelation, combatStats):
	eligibleStats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
	# in base stat relation, highest stat must always remain higher than lower stats
	# EG. if speed is 10 and attack is 9, and speed is higher (NOT equal) in BSR than attack, attack CANNOT be raised
	# EG. if speed is 10 and attack is 9, and speed is equal in BSR to attack, either attack or speed CAN be raised at will (as long as they don't exceed a higher BSR tier)
	# methodology:
	# check lowest tiers first; they're the ones that are going to be disqualified
	# check a stat 'currentStat'
	# loop through all stats
	# if stat is currentStat, disregard
	# if stat is in lower tier, disregard (should just be able to check that the stat hasn't previously been checked, since we check lower tiers beforehand)
	# if stat is in current tier, disregard
	# if stat is in higher tier, check that currentStat is at least -2 from items
	# if currentStat is -1 or above to stat in higher tier, remove from eligibleStats
	checkedStats = []
	for tier in reversed(range(len(baseStatRelation))):
		# tier counts from len to 0; lowest tier to highest
		#print(baseStatRelation[tier])
		for currentStat in baseStatRelation[tier]:
			for stat in combatStats:
				# ignore stats in lower tier than this one; we can do this by ignoring already-checked stats, since we check tiers in order lowest to highest
				if stat not in checkedStats:
					# ignore other stats within the same tier
					if stat not in baseStatRelation[tier]: 
						# remaining stats are higher-tier stats
						if combatStats[currentStat] >= combatStats[stat]-1:
							eligibleStats.pop(eligibleStats.index(currentStat))
							break
			checkedStats.append(currentStat)
	return eligibleStats

# pokemon is the dict() pokemon, levels is how many levels to gain
def levelPokemon(pokemon, levels):
	for i in range(levels):
		# increment level
		pokemon['level'] = pokemon['level'] + 1
		# check if a move can be learned
		levelMoves = getPokemonLevelMoves(pokemon['species'])
		for move in levelMoves:
			if int(levelMoves[move]) == pokemon['level']:
				if len(pokemon['movesLearned']) < 6:
					pokemon['movesLearned'].append(move)
				else:
					# deal with working out whether to forget a move in exchange for the new move here
					# just a random 50/50 chance for now; once moves_105.ini is complete it might look at whether attack or special_attack is used and prioritise stuff based on the higher attack value
					# or if roughly the same try to make sure it has at least one special attack move and one attack move
					remove = random.choice(True, False)
					if remove:
						pokemon['movesLearned'].pop(pokemon['movesLearned'].index(random.choice(pokemon['movesLearned']))) # get the index of a random move in pokemon['movesLearned'] and pop it from the list
						pokemon['movesLearned'].append(move)
		# check if it got a tutor point
		if pokemon['level'] % 5 == 0:
			pokemon['tutorPoints'] = pokemon['tutorPoints']+1
		# check if can evolve, and do that; also, reapply nature to base stats and recalculate base stat relation and restat the thing
		# pokemon may learn any moves its earlier form could not, below the minimum level for the evolution (so if evolution is delayed and that skips a move, the pokemon does NOT get the chance to learn it)
		# add stat point
		eligibleStats = getImprovableStats(pokemon['baseStatRelation'], pokemon['combatStats'])
		# currently doesn't have any plan, just raises a random eligible stat
		stat = random.choice(eligibleStats)
		pokemon['combatStats']['stat'] = pokemon['combatStats']['stat'] + 1
	return pokemon

# legendary and fossil: False, True or None? False disallows it, True means it must be, and None means it can be?
# TO-DO: just make this call the filter method directly, rather than go through getFilteredPokemonList
# or write another method that does that, as constructing strings for getFilteredPokemonList sucks
# rename getFilteredPokemonList getFilteredPokemonListFromString, too.
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
	if 'None' not in getPokemonEggGroups(a) and 'None' not in getPokemonEggGroups(b):
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
			printTrainer(generateRandomTrainer())
		elif generatorMenu == "2": # Random Pokemon
			printPokemon(generatePokemon())
	else:
		mainMenu = "-1"