


import sys, numpy, re
from itertools import permutations, combinations
from pprint import pformat

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

    def set_tile(self, row, column, char):
        self.surface[row, column] = ord(char.lower())
        self.surface[row, column] = ord(char.lower())

    def get_spaces(self):
        spaces = []
        for column in range(self.width):
            s = self.surface
            # describe the constraints on this column/row
            env = []
            for row in range(board.height):
                env.append(self.get_word_LR(row, column))
            raw_input(pformat(env))

            # figures out what letters are possible in this column
            constraint_strings = []
            for row in range(board.height):
                if len(env[row]) > 1:
                    constraint_strings.append(self.get_letters_could_fit(env[row]))
                else:
                    constraint_strings.append(env[row])
            print constraint_strings

            # create spaces (contiguous combinations of spots)
            # get a list like this:
            #['?', '?', '?', '?', '?', [], [], [a], 'd', 'u', 'c', 'k', '?', '?', '?']
            # where letters are already there, blanks are ?, and lists are possible
            # letters that could go there.
            # in-line constraints have not been dealt with yet (the fact that
            # only 'y' works after 'duck' here isn't yet known.

            # spaces have to grow off of something - either a list or a letter.
            spaces = self.make_spaces_from_constraints(constraint_strings)

    def make_spaces_from_constraints(self, constraints):
        """Returns a space for each possible combination of blanks"""
        # get a list like this:
        #['?', '?', '?', '?', '?', [], [], [a], 'd', 'u', 'c', 'k', '?', '?', '?']
        

    def split_constraints_by_blocks

    def get_letters_could_fit(self, blank_string):
        """Returns what of my_letters could be in a spot"""
        work = []
        for letter in self.my_letters_set:
            # only bother checking for letters I have
            check = blank_string.replace('?',letter)
            if check in self.dictionary:
                work.append(letter)
        return work

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

    def __getitem__(self, i):
        return self.board[i]

class Space():
    """A block of spots tiles could be placed, with constraints"""
    def __init__(self, list_of_pos):
        pass



if __name__ == '__main__':
    s = open('ryan2.PNG.code').read().replace('\n','').replace('6',' ').replace('5',' ').replace('3',' ').replace('2',' ')
    board = WWF(s, 'abcdefm')
    #board.set_tile(3, 3,'d')
    #board.set_tile(3, 4,'m')
    #board.set_tile(3, 5,'d')
    #board.set_tile(6, 6,'H')
    #board.set_tile(6, 7,'A')
    print board
    board.get_spaces()
    #print board.get_horizontal_word(3,3)
