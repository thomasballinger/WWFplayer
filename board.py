#!/usr/bin/env python

# I'm excited to write tests so I can rip this thing's guts out,
# but even the structure sucks at this point
# Would require some restructuring for the concept of
# wild-card blank tiles

import sys
import numpy
import re
from itertools import permutations, combinations, product
from pprint import pformat, pprint
import sys
from operator import mul

class WWF():
    """WWF Game"""

    #Replacing self.surface indexing with this function call added added 0.02s to my test case.
    #It is called by get_word_LR_or_UD(...).
    def tile_at(self, row, col):
        return chr(self.surface[row,col])

    def width(self, surface):
        return surface.shape[0]

    def height(self, surface):
        return surface.shape[1]

    def make_surface(self, board_file, width, height):
        with open(board_file) as f:
            status_string = f.read().replace('\n','').replace('6',' ').replace('5',' ').replace('3',' ').replace('2',' ').replace('*',' ').replace('4',' ')
        return numpy.array([ord(x.lower()) for x in status_string ]).reshape((width, height))

    def make_dictionary(self, dictionary_files):
        #TODO: does this have an advantage over reading them into lists and combining?
        return set( sum( [re.split(r"[\r\n]+", open(fn).read()) for fn in dictionary_files], []) )

    def make_points_dict(self):
        return dict(zip( 'a b c d e f g h i j  k l m n o p q  r s t u v w x y z '.split(), 
                        [1,4,4,2,1,4,3,3,1,10,5,2,4,2,1,4,10,1,1,1,2,5,4,8,3,10]))

    def make_board(self, blank_board_file, width, height):
        return numpy.array([ord(x) for x in open('./board_blank.txt').read().replace('\n','')]).reshape((width, height))

    # positions are described as (y, x) pairs, top left is 0,0!
    def __init__(self, board_file, tiles, dictionary_files=('dictionary.txt', 'customwords.txt'), size=(15,15), board_string=None):
        self.surface = self.make_surface(board_file, size[0], size[1])
        self.my_letters = [x for x in tiles]
        self.dictionary = self.make_dictionary(dictionary_files)
        self.points_dict = self.make_points_dict() 
        self.board = self.make_board('board_blank.txt', size[0], size[1])
        self.board_letter_multipliers = {51 : 3, 50 : 2}
        self.board_word_multipliers   = {54 : 3, 52 : 2}
        print self.board

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
            #print self
            #print move
            if move[2][1] - move[1][1] == 1:
                #print 'main word is vertical'
                word_goes_vertical = True
            else:
                #print 'main word is horizontal'
                word_goes_vertical = False
            words = [[move[0], move[1], move[2]]]
            for i,x in [(i, x) for i, x in enumerate(move[3]) if type(x) == type([])]:
                #print i,x

                if word_goes_vertical:
                    word = self.get_word_LR(move[1][0]+i, move[1][1])
                    #print 'word with ? in it:', word
                    q_index = word.find('?')
                    #print 'len of word:', len(word)
                    #print 'index of ?:', q_index
                    (top, left) = (move[1][0]+i, move[1][1] - q_index)
                    #print 'move[1][1]', move[1][1],'- len(word)', len(word), '+q_index',q_index,'+2',2
                    (bottom, right) = (top+1, left + len(word))
                else:
                    word = self.get_word_UD(move[1][0], move[1][1]+i)
                    q_index = word.find('?')
                    (top, left) = (move[1][0] - q_index, move[1][1]+i)
                    (bottom, right) = (top+len(word), left + 1)
                word = word.replace('?', move[0][i])
                #print word, (top, left), (bottom, right)
                words.append([word, (top, left), (bottom, right)])
            # apply letter bonuses
            word_spots = [(i,j) for i in range(move[1][0], move[2][0]) for j in range(move[1][1], move[2][1])]
            #print 'word_spots', word_spots
            new_word_spots = [(i,j) for i,j in word_spots if self.surface[i, j] in [32]]
            #print 'new_word_spots', new_word_spots
            spots_of_words = [words[0] + [word_spots, new_word_spots]]
            #print 'words:', words
            for word in words[1:]:
                #print 'word:', word
                word_spots = [(i,j) for i in range(word[1][0], word[2][0]) for j in range(word[1][1], word[2][1])]
                #print 'word_spots', word_spots
                new_word_spots = [(i,j) for i,j in word_spots if self.surface[i, j] in [32]]
                #print [self.surface[i,j] for i,j in word_spots]
                #print 'new_word_spots', new_word_spots
                spots_of_words.append(word + [word_spots, new_word_spots])
            #print spots_of_words
            point_sum = 0
            #if len(words)>1:
            #    raw_input()
            for word in spots_of_words:
                #print 'word', word
                #print word[3]
                base_points = [self.points_dict[letter]*self.board_letter_multipliers.get(spot, 1) for letter, spot in zip(word[0], word[3])]
                multiplier   = reduce(mul, [self.board_word_multipliers.get(spot, 1) for letter, spot in zip(word[0], word[3])])
                total = sum(base_points) * multiplier
                #print word[0], ': sum of', base_points, 'x', multiplier, '=', total
                point_sum += total
            if len(spots_of_words[0][-1]) == len(self.my_letters):
                #print 'bonus! +30'
                point_sum += 30
            if words == [['ab', (6, 13), (8, 14)], ['saga', (6, 14), (7, 18)]]:
                raw_input()
            #print 'total', point_sum

            # for each new word created (obvious one and any others)
            #   apply all applicable letter bonuses
            #   apply all applicable word bonuses
            # add these all up
            # add bonus if all 7 tiles used
            scored_moves.append((total, move))
        scored_moves.sort()
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
        could go here.
        """

        s = self.surface

        spaces = []

        for column in range(self.width(s)):
            # first we describe the constraints on this row
            env = [self.get_word_LR(row, column) for row in range(self.height(s))]
            # figures out what letters are possible in each spot of this column
            constraints = [self.get_letters_could_fit(env[row]) if len(env[row])>1 else env[row] for row in range(self.height(s))]
            for ind_space in self.get_1D_spaces(constraints):
                spaces.append(((ind_space[0],column),(ind_space[1],column+1), constraints[ind_space[0]:ind_space[1]]))

        for row in range(self.height(s)):
            env = [ self.get_word_UD(row, column) for column in range(self.width(s)) ]
            constraints = [self.get_letters_could_fit(env[row]) if len(env[column])>1 else env[column] for column in range(self.width(s))]
            for ind_space in self.get_1D_spaces(constraints):
                spaces.append(((row, ind_space[0]),(row+1, ind_space[1]),
                    constraints[ind_space[0]:ind_space[1]]))

        return spaces

    def find_moves_from_spaces(self, spaces):
        """Produces moves like ('word', (row, column), (row, column))"""
        # TODO refactor such that we don't have to store all so much in memory;
        # should be generators at both levels, not making a list of valid
        # constrained combinations before trying anything

        moves = []
        for space in spaces:
            (t, l), (b, r), c = space
            if len(c) == 1:
                # then we'll catch this word when we're doing this perpendicular ones,
                # in which it would show up as something longer (including the 
                # letters it's building off of)
                continue
            bare_build_string = [letter if letter in list('abcdefghijklmnopqrstuvwxyz') else None
                    for letter in c]
            # first produce all combinations of constrained tiles

            free_stuff = [(i,x) for i,x in enumerate(c) if x == '?']
            if free_stuff:
                free_indices, free_tiles = zip(*free_stuff)

            constrained_stuff = [(i,x) for i,x in enumerate(c) if type(x) == type([])]
            if constrained_stuff:
                constrained_indices, constrained_tiles = zip(*constrained_stuff)

                valid_const_combs = []
                for comb in product(*constrained_tiles):
                    letters = self.my_letters[:]
                    try:
                        for letter in comb:
                            letters.remove(letter)
                        valid_const_combs.append((comb, letters[:],))
                    except ValueError:
                        continue
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
                            moves.append((word, (t, l), (b, r), c))
            elif constrained_stuff:
                if not valid_const_combs:
                    continue
                for comb, letters_leftover in valid_const_combs:
                    build_string = bare_build_string[:]
                    for i, tile in zip(constrained_indices, comb):
                        build_string[i] = tile
                    word = "".join(build_string)
                    if word in self.dictionary:
                        moves.append((word, (t, l), (b, r), c))
            elif free_stuff:
                for perm in permutations(self.my_letters, c.count('?')):
                    build_string = bare_build_string[:]
                    for i, tile in zip(free_indices, perm):
                        build_string[i] = tile
                    word = "".join(build_string)
                    if word in self.dictionary:
                        moves.append((word, (t, l), (b, r), c))
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

        # now sections these spans up into groups that end before blanks or ends
        spaces = []
        for span in spans:
            sub = s[span[0]:span[1]]
            blank_spans = []
            for l in range(span[1] - span[0]):
                for d in range(1, (span[1] - span[0]) - l + 1):
                    subsub = ('|'+sub+'|')[l:l+d+2]
                    # if surrounded by blanks or blocks, with a blank seed somewhere:
                    if re.match(r"[|&?][a-z?&]*[&][a-z?&]*[|&?]$", subsub):
                        space = (l+span[0], d+l+span[0], s[l+span[0]:d+l+span[0]])
                        spaces.append(space)
                        #sub_space = [(l, d+l, sub[l:d+l])]
                    # if surounded by blanks or blocks, with a next-to-letter seed somewhere:
                    elif re.match(
                            r"[|&?][a-z?&]*[a-z][?&][a-z?&]*[|?&]$"
                            "|"
                            r"[|&?][a-z?&]*[?&][a-z][a-z?&]*[|?&]$",
                            subsub):
                        space = (l+span[0], d+l+span[0], s[l+span[0]:d+l+span[0]])
                        spaces.append(space)
                    else:
                        pass

        # Now we cut out spaces which are too long for the player's letters
        spaces_with_less_blanks_than_my_letters = [
                space for space in spaces
                if len([letter for letter in s[space[0]:space[1]]
                    if letter in '?&']) <= len(self.my_letters)]
        return spaces_with_less_blanks_than_my_letters

    def get_letters_could_fit(self, blank_string):
        """Returns what of my_letters could be in a '?' marked spot"""
        return [letter for letter in set(self.my_letters) if blank_string.replace('?',letter) in self.dictionary]
        
    def get_word_LR_or_UD(self, row, col, orientation):
        """Returns string contents of spot, with letters around it if blank"""
        if self.tile_at(row,col) != ' ':
            return self.tile_at(row,col)
        if orientation == 'LR':
            tile_row = list(self.surface[row, :])
            tile_row[col] = ord('?')
        elif orientation == 'UD':
            tile_row = list(self.surface[:, col])
            tile_row[row] = ord('?')
        row_string = ''.join([chr(x) for x in tile_row])
        #TODO PROFILE is regex an efficient solution here?
        return re.search(r'([^ ]*[?][^ ]*)', row_string).group(1)

    def get_word_LR(self, row, col):
        return self.get_word_LR_or_UD(row, col, 'LR')

    def get_word_UD(self, row, col):
        return self.get_word_LR_or_UD(row, col, 'UD')

def main():
    #s2 = ' '*15*3 + ' a  b  e       '+ ' '*15*2+'this is great  '+' '*15*8
    #print len(s2)
    #board = WWF(s2, 'abcdefg')
    #print board
    #pprint(board.score_moves(board.find_moves_from_spaces(board.get_spaces())))
    #raw_input("Press Enter")
    import time
    tic = time.time()
    board = WWF(sys.argv[1], sys.argv[2])
    pprint( board.score_moves( board.find_moves_from_spaces(board.get_spaces()) ) )
    toc = time.time()
    print board
    print 'time: ' + str(toc - tic)

if __name__ == '__main__':
    main()
