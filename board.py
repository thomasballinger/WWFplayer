# I'm excited to write tests so I can rip this thing's guts out,
# but even the structure sucks at this point
# Would require some restructuring for the concept of
# wild-card blank tiles

import sys, numpy, re
from itertools import permutations, combinations, product
from pprint import pformat, pprint
import sys

def debug_message(*msg):
    sys.stdout.write(" ".join([str(x) for x in msg])+'\n')

def do_nothing(*args):
    pass

debug = False
if debug:
    v = debug_message
else:
    v = do_nothing

class WWF():
    """WWF Game"""
    # positions are described as (y, x) pairs!
    # 0 to 14 left to right, top to bottom
    def __init__(self, status_string, tiles):
        self.width = 15
        self.height = 15
        self.surface = numpy.array([ord(x.lower()) for x in status_string ]).reshape((self.width, self.height))
        self.width, self.height = self.surface.shape
        self.board = numpy.zeros(self.surface.shape)
        self.my_ords = [ord(x) for x in tiles]
        self.my_letters = [x for x in tiles]
        self.my_letters_set = set(self.my_letters)
        self.dictionary = set(open('./enable1.txt').read().split('\r\n'))

    def __str__(self):
        return '\n'.join([' '.join([chr(x).upper() if x else '-' for x in row]) for row in self.surface])

    def score_moves(self, moves):
        """Returns moves as (score, move) tuples"""
        #
        #  Stub for Ryan to write
        #
        # moves look like this:
        # ((top, left), (bottom+1, right+1), word)
        # example:
        # ('apples', (2, 5), (3, 12))
        # 
        # self.board should contain the board information,
        # it's not used for anything else yet so the 
        # format could be changed.  Right now
        # it's a numpy array of identical dimensions to the
        # self.surface numpy array which contains tile information
        # This should also check to see if all letters are
        # being used for the 30 point bonus - more information
        # could be passed along to this function, since that's
        # basically already known before this.
        scored_moves = []
        for move in moves:
            scored_moves.append((42, move))
        return scored_moves

    def set_tile(self, row, column, char):
        self.surface[row, column] = ord(char.lower())
        self.surface[row, column] = ord(char.lower())

    def get_spaces(self):
        """Returns all groups of spots where letters could be put.

        Format of output is ((top, left), (bottom+1, right+1), constraints)
        where constraints is a description of the environment.

        Constraints are of the form:
        ['?', [], [], [a, b], 'd', 'u', 'c', 'k', '?', '?', '?']
        where '?' means empty, 'a' means that letter is already in that spot,
        [a, b] means that of the letters this player holds, only one of these
        letters could go here, and [] means that no letter this player holds
        could go here."""

        s = self.surface

        spaces = []
        for column in range(self.width):
            # first we describe the constraints on this row
            env = []
            for row in range(board.height):
                env.append(self.get_word_LR(row, column))

            # figures out what letters are possible in each spot of this column
            constraints = []
            for row in range(board.height):
                if len(env[row]) > 1:
                    constraints.append(self.get_letters_could_fit(env[row]))
                else:
                    constraints.append(env[row])
            v(constraints)

            ind_spaces = self.get_1D_spaces(constraints)
            v(ind_spaces)

            for ind_space in ind_spaces:
                v(ind_space)
                spaces.append(((ind_space[0],column),(ind_space[1],column+1),
                    constraints[ind_space[0]:ind_space[1]]))
                v(spaces[-1])

        for row in range(self.height):
            env = []
            for column in range(board.width):
                env.append(self.get_word_UD(row, column))

            constraints = []
            for column in range(board.width):
                if len(env[column]) > 1:
                    constraints.append(self.get_letters_could_fit(env[row]))
                else:
                    constraints.append(env[column])
            v(constraints)

            ind_spaces = self.get_1D_spaces(constraints)

            v(ind_spaces)

            for ind_space in ind_spaces:
                spaces.append(((row, ind_space[0]),(row+1, ind_space[1]),
                    constraints[ind_space[0]:ind_space[1]]))
                v(spaces[-1])

        return spaces

    def find_moves_from_spaces(self, spaces):
        """Produces moves like ('word', (row, column), (row, column))"""
        # TODO refactor such that we don't have to store all so much in memory;
        # should be generators at both levels, not making a list of valid
        # constrained combinations before trying anything

        moves = []
        for space in spaces:
            (t, l), (b, r), c = space
            v('constraints:', c)
            if len(c) == 1:
                # then we'll catch this word when we're doing this perpendicular ones,
                # in which it would show up as something longer (including the 
                # letters it's building off of)
                continue
            bare_build_string = [letter if letter in list('abcdefghijklmnopqrstuvwxyz') else None
                    for letter in c]
            v('bare build string:', bare_build_string)
            # first produce all combinations of constrained tiles

            free_stuff = [(i,x) for i,x in enumerate(c) if x == '?']
            if free_stuff:
                free_indices, free_tiles = zip(*free_stuff)
                v('free tiles:', free_tiles)

            constrained_stuff = [(i,x) for i,x in enumerate(c) if type(x) == type([])]
            if constrained_stuff:
                constrained_indices, constrained_tiles = zip(*constrained_stuff)
                v('constrained tiles:', constrained_tiles)

                valid_const_combs = []
                for comb in product(*constrained_tiles):
                    v('comb', comb)
                    letters = self.my_letters[:]
                    try:
                        for letter in comb:
                            v('letter',letter)
                            v('letters', letters)
                            letters.remove(letter)
                        valid_const_combs.append((comb, letters[:],))
                        v('comb', comb, 'checks out as ok')
                    except ValueError:
                        v('cannot make that letter combination with these tiles!')
                        continue
                v('valid constrained tile combinations:', valid_const_combs)
            else: # no constained tiles in constraint
                pass

            # for each of these, produce all perms of all combs of tiles
            if constrained_stuff and free_stuff:
                if not valid_const_combs:
                    continue
                for comb, letters_leftover in valid_const_combs:
                    for perm in permutations(letters_leftover, c.count('?')):
                        build_string = bare_build_string[:]
                        for i, tile in zip(constrained_indices, comb):
                            build_string[i] = tile
                        for i, tile in zip(free_indices, perm):
                            build_string[i] = tile
                        word = "".join(build_string)
                        if word in self.dictionary:
                            v(word, 'found in dictionary!')
                            moves.append((word, (t, l), (b, r)))
            elif constrained_stuff:
                if not valid_const_combs:
                    continue
                for comb, letters_leftover in valid_const_combs:
                    build_string = bare_build_string[:]
                    for i, tile in zip(constrained_indices, comb):
                        build_string[i] = tile
                    word = "".join(build_string)
                    if word in self.dictionary:
                        v(word, 'found in dictionary!')
                        moves.append((word, (t, l), (b, r)))
            elif free_stuff:
                for perm in permutations(self.my_letters, c.count('?')):
                    build_string = bare_build_string[:]
                    for i, tile in zip(free_indices, perm):
                        build_string[i] = tile
                    word = "".join(build_string)
                    if word in self.dictionary:
                        v(word, 'found in dictionary!')
                        moves.append((word, (t, l), (b, r)))
            else:
                raise Exception('WTF just happened?')

        return moves

    def get_1D_spaces(self, constraints):
        """Returns a space for each possible combination of blanks.

        Only spaces which could work for the players letters are returned.
        Produces (start_index, stop_index, 'magic string'), like
        (3, 11, '??&??ab?')"""
        #TODO: should compile these regex's (not that bad though - just runs 30 times per turn)

        # giving a regex approach a try (if you've got a hammer...)
        s = "".join(str(x) if x in list('abcdefghijklmnopqrstuvwxyz?') else '|' if x == [] else '&' for x in constraints)
        v(s)
        # now we have something like this, one character per spot
        # '?????|&&duck???'
        # from which we want all the sections containing seeds
        spans = []

        #TODO: couldn't these be combined?  The issue is that I can only
        # get the indexes of the whole match from the match object, and 
        # if theres a ([|]|$) in there whether I need to step the index
        # forward or not changes.

        # beginning to block ([] is a block)
        sections = list(re.finditer(r"$([a-z?&]*(?:[&]|[a-z][?]|[?][a-z])[a-z?&]*)[|]", s))
        spans += [(0, x.span()[1]-1) for x in sections]

        # block to block
        sections = list(re.finditer(r"[|]([a-z?&]*(?:[&]|[a-z][?]|[?][a-z])[a-z?&]*)[|]", s))
        spans += [(x.span()[0]+1, x.span()[1]-1) for x in sections]

        # block to end
        sections = list(re.finditer(r"[|]([a-z?&]*(?:[&]|[a-z][?]|[?][a-z])[a-z?&]*)$", s))
        spans += [(x.span()[0]+1, x.span()[1]) for x in sections]

        # start to end
        sections = list(re.finditer(r"^([a-z?&]*(?:[&]|[a-z][?]|[?][a-z])[a-z?&]*)$", s))
        spans += [(x.span()[0], x.span()[1]) for x in sections]

        v('full symbolic string from which spans are found:', s)
        v('full spans: (these will be further examined for valid blank sections)')
        for span in spans:
            v(span, s[span[0]:span[1]])
        if not spans:
            v('no spans found')

        # now sections these spans up into groups that end before blanks or ends
        spaces = []
        for span in spans:
            sub = s[span[0]:span[1]]
            v('minispans of', sub)
            blank_spans = []
            for l in range(span[1] - span[0]):
                for d in range(1, (span[1] - span[0]) - l + 1):
                    subsub = ('|'+sub+'|')[l:l+d+2]
                    v(len(sub),l,d+l,subsub)
                    # if surrounded by blanks or blocks, with a blank seed somewhere:
                    if re.match(r"[|&?][a-z?&]*[&][a-z?&]*[|&?]$", subsub):
                        space = (l+span[0], d+l+span[0], s[l+span[0]:d+l+span[0]])
                        spaces.append(space)
                        v('     Looks Legit by blank seed!')
                        #sub_space = [(l, d+l, sub[l:d+l])]
                        v(space)
                    # if surounded by blanks or blocks, with a next-to-letter seed somewhere:
                    elif re.match(
                            r"[|&?][a-z?&]*[a-z][?&][a-z?&]*[|?&]$"
                            "|"
                            r"[|&?][a-z?&]*[?&][a-z][a-z?&]*[|?&]$",
                            subsub):
                        space = (l+span[0], d+l+span[0], s[l+span[0]:d+l+span[0]])
                        spaces.append(space)
                        v('     Looks Legit by touching seed!')
                    else:
                        v(' not legit')

        # Now we cut out spaces which are too long for the player's letters
        v(spaces)
        spaces_with_less_blanks_than_my_letters = [
                space for space in spaces
                if len([letter for letter in s[space[0]:space[1]]
                    if letter in '?&']) <= len(self.my_letters)]
        v(len(spaces), 'cut down to', len(spaces_with_less_blanks_than_my_letters), 'by keeping them short')
        v('(I have', len(self.my_letters), 'letters)')
        v(spaces_with_less_blanks_than_my_letters)
        return spaces_with_less_blanks_than_my_letters

    def get_letters_could_fit(self, blank_string):
        """Returns what of my_letters could be in a '?' marked spot"""
        work = []
        for letter in self.my_letters_set:
            # only bother checking for letters I have
            check = blank_string.replace('?',letter)
            if check in self.dictionary:
                work.append(letter)
        return work

    #TODO combine these two functions, they have like 2 differences
    def get_word_LR(self, row, column):
        """Returns string contents of spot, with letters around it if blank"""
        s = self.surface
        tile_at_spot = s[row, column]
        if tile_at_spot != 32:
            return chr(tile_at_spot)
        tile_row = list(self.surface[row, :])
        tile_row[column] = 63
        row_string = ''.join([chr(x) for x in tile_row])
        #TODO PROFILE is regex an efficient solution here?
        return re.search(r'([^ ]*[?][^ ]*)', row_string).group(1)

    def get_word_UD(self, row, column):
        """Returns string contents of spot, with letters around it if blank"""
        s = self.surface
        tile_at_spot = s[row, column]
        if tile_at_spot != 32:
            return chr(tile_at_spot)
        tile_row = list(self.surface[:, column])
        tile_row[row] = 63
        row_string = ''.join([chr(x) for x in tile_row])
        #TODO PROFILE is regex an efficient solution here?
        return re.search(r'([^ ]*[?][^ ]*)', row_string).group(1)

if __name__ == '__main__':
    s2 = ' '*100+'this is great  '+' '*110
    s = open('ryan2.PNG.code').read().replace('\n','').replace('6',' ').replace('5',' ').replace('3',' ').replace('2',' ')
    board = WWF(s, 'abcdefg')
    print board
    pprint(board.score_moves(board.find_moves_from_spaces(board.get_spaces())))
    board = WWF(s2, 'abcdefg')
    print board
    pprint(board.score_moves(board.find_moves_from_spaces(board.get_spaces())))
