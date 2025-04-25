
import random
import string
import math

MAXIMUM_LENGTH = 100_000 # Absolute maximum length of the generated data.

ALLOWED_CHARS = string.printable # All allowed characters.

PUNCTUATION_CHANCE = 0.9

# ALLOWED_CHARS = ["(", ")"]

NEW_DATA_CHANCE = 0.01 # Possibility of creating an entirely new string.

MAX_REPEAT_COUNT = 100_00 # Maximum amount of repetitions

MAX_REPEAT_LENGTH = 10000 # Maximum length of the repeating stuff

MAX_REPEAT_COUNT_LINEAR = 10000

MIN_REPEAT_COUNT_LINEAR = 200

MAX_REPEAT_TOKEN_LENGTH = 5 # Maximum length of the string which to repeat.

MAX_REPEAT_STRING_COUNT = 10 # Maximum amount of repeated strings, for example if we have three of these then this will generate a string like "ababababccccccccccccccqwertyqwertyqwerty" (three repeating substrings)

EXISTING_SUBSTRING_CHANCE = 0.95 # Change to get an existing substring from the string


MAX_SUBSTRING_LENGTH = 10

REPLACE_CHANCE = 0.3 # Chance to replace the original shit string. If not this, then the data will be inserted at a random index.

def f(x: float) -> float: # Function (for now this is "(x + 0.1) ** 10") (this is assumed to be growing in the period 0 <= x <= 1)
	return (x + 0.6) ** 3 + max(MIN_REPEAT_COUNT_LINEAR, round(MAX_REPEAT_COUNT_LINEAR * x))

THING = f(1.0) # Precalculated


def dist_function(x: float) -> float: # Distribution. x is assumed to be between 0 <= x <= 1
	assert 0 <= x <= 1
	return f(x) / THING # Random value divided by maximum value. (Maximum is assumed to be at x = 1)




def distribution(c: int) -> int: # Returns a random number (max is c and minimum is zero). This function is biased against small numbers (the probability of generating a relatively small number is high, whileas the probability of generating a comparatively large number is small.)
	return round(c * dist_function(chance()))

# def custom_mutator()


def custom_mutator(data, max_size, seed, native_mutator):
	# Just call mutate and see what happens...
	if isinstance(data, bytearray):
		convert = True
		data = bytes(data)
	new_data = mutate(data)
	if convert:
		new_data = bytearray(new_data)
	if len(new_data) >= max_size:
		return new_data[:max_size] # Just add a cutoff
	return new_data


def chance() -> float: # Shorthand
	return random.random()

def c(const: float) -> bool: # Rolls a dice and returns true with a probability of "const"
	return chance() <= const

def rnum(n: int) -> int: # Shorthand
	if n == 0 or n == -1:
		return 0
	return random.randrange(0, n)

def stringmult(string: bytes, c: int) -> bytes: # Multiplies string by c times.

	count = min(math.floor(MAX_REPEAT_LENGTH/len(string)), c)
	assert isinstance(count, int)

	out = string * count
	assert len(out) <= MAX_REPEAT_LENGTH

	return out

	#return (string * c)[:MAXIMUM_LENGTH] # Just automatically truncate the string

def rand_ascii_string(n: int) -> bytes: # Generates n random ascii bytes (taken from string.printable)
	#if c(PUNCTUATION_CHANCE):
	#	return bytes([ord(random.choice(string.punctuation)) for _ in range(n)])
	return bytes([ord(random.choice(string.printable)) for _ in range(n)]) # Create array of allowed bytes and convert to bytes

def generate_repeating(n: int) -> bytes: # Generate a random repeating string and repeat it n times
	#return stringmult(rand_ascii_string(rnum(MAX_REPEAT_TOKEN_LENGTH)), n)
	return stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), n)

def generate_new() -> bytes: # Generate a new ascii string.
	repeat_count = rnum(MAX_REPEAT_STRING_COUNT)

	out = b"" # Final generated string

	for i in range(repeat_count): # Generate "repeat_count" repeating strings.

		out += generate_repeating(rnum(MAX_REPEAT_COUNT))

	return out

def get_substr(data: bytes) -> bytes:
	rand_ind = min(rnum(len(data)), MAX_SUBSTRING_LENGTH)
	#length = distribution(len(data[rand_ind:])-1) # The length should be based on a certain distribution
	length = rnum(len(data[rand_ind:])-1)
	#print("length == "+str(length))
	res = data[rand_ind:rand_ind+length]
	#print("res == "+str(res))
	return res, rand_ind # Return the substring






def mutate_existing(data: bytes) -> bytes:

	# Mutation count:

	# Get a random substring and then multiply it and then put it into a random place.

	# substr, rand_ind = get_substr(data) if c(EXISTING_SUBSTRING_CHANCE) else (None, None)

	substr, rand_ind = get_substr(data) if True else (None, None)

	if True and substr:
		# Just cut out the original string and then add the multiplied substring in there.
		#assert substr in data # Sanity checking

		rep_count = distribution(MAX_REPEAT_COUNT)
		#print("stringmult(substr, distribution(MAX_REPEAT_COUNT)) == "+str(stringmult(substr, rep_count)))
		#print("substr == "+str(substr))
		#print("rep_count == "+str(rep_count))
		multiplication = stringmult(substr, rep_count)
		#print("multiplication == "+str(multiplication))
		#if b"("*1000 in multiplication:
		#	print("!!!")
		#	data = data[place_index:] + multiplication + data[place_index:]
		#	print("data == "+str(data))
		#	exit(0)

		data = data[:rand_ind] + multiplication + data[rand_ind+len(substr):]
		#print("data == "+str(data))

		return data
	else:
		# Place somewhere else.

		#assert substr in data # Sanity checking
		place_index = rnum(len(data)-1)
		#assert place_index != -1
		#data = data.replace(substr, b"") # Remove the data
		rep_count = distribution(MAX_REPEAT_COUNT)
		#print("stringmult(substr, distribution(MAX_REPEAT_COUNT)) == "+str(stringmult(substr, rep_count)))
		#print("substr == "+str(substr))
		#print("rep_count == "+str(rep_count))

		multiplication = stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), rep_count)

		#print("multiplication == "+str(multiplication))

		'''
		if b"("*1000 in multiplication:
			print("!!!")
			data = data[place_index:] + multiplication + data[place_index:]
			print("data == "+str(data))
			exit(0)
		'''

		data = data[place_index:] + multiplication + data[place_index:]

		return data



	return data




def mutate(data: bytes): # Main mutator entry point. Returns a mutated version of the data.
	# fh = open("stuff.txt", "a+")
	# fh.write("Called the shit...")
	# fh.close()
	# print("calling the mutator")
	if c(NEW_DATA_CHANCE): # Create new string.
		return generate_new()
	else: # Mutate existing.
		return mutate_existing(data)

def fuzz(buf, add_buf, max_size): # For AFL and AFL++

	data = buf

	#print(str(type(data)) * 100)

	#assert (isinstance(data, bytes))

	data = bytes(data) # Convert bytearray to bytes.

	data = mutate(data)

	if len(data) >= max_size:
		print("Truncating returned fuzz data...\n")
		print("Orig len is " + str(len(data)) + " . New len is " + str(max_size))
		data = data[:max_size] # Truncate

	data = bytearray(data) # Convert bytes back to bytearray.

	return data


def deinit(): # AFL and AFL++ complain if we do not have this for some reason...
	pass

if __name__=="__main__": # For testing only (well, fuzzing is testing, but you know what I mean :D )
	#print("random.choice(ALLOWED_CHARS) == "+str(random.choice(ALLOWED_CHARS)))
	#print(rand_ascii_string(10)) # Generate a random string

	MAX_MUT_COUNT = 2000

	#while True:

	TEST_COUNT = 100000

	#for _ in range(TEST_COUNT):

	BRACE_COUNT = 100

	favored_count = 0
	tot_count = 0
	favored_count2 = 0
	while True:
		
		#print("tot_count == "+str(tot_count))
		mut_count = rnum(MAX_MUT_COUNT)
		#mut_count = 1
		res = b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
		for _ in range(mut_count):
			#print("tot_count == "+str(tot_count))
			tot_count += 1
			res = mutate_existing(res)
			if len(res) > MAXIMUM_LENGTH: # Bounds check
				res = res[:MAXIMUM_LENGTH]
			#print("len(res) == "+str(len(res)))
			if b")"*BRACE_COUNT in res:
				#print("first case!!!")
				favored_count += 1
				if b"("*BRACE_COUNT in res:
					print("second case!!!!")
					print(res)
					exit(1)

			if b"("*BRACE_COUNT in res:
				favored_count2 += 1

			if tot_count % 1_000_000 == 0:
				print(favored_count / tot_count)
				print("favored2: "+str(favored_count2 / tot_count))
		#print(mutate_existing(b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"))
		#print(res)
		#print("len(res) == "+str(len(res)))
		#if b"("*1000 in res and b")"*1000 in res:

	

	'''

	orig_contents = b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

	while True:
		contents = orig_contents
		mut_count = rnum(MAX_MUT_COUNT)
		for _ in range(mut_count):
			contents = mutate(contents)

	'''


	exit(0) # Return succesfully


