#  Originally from Kevan Hong-Nhan Nguyen 71632979.  ICS 32 Lab sec 9.  Project #5.

import numpy as np

# Cell states
NONE = 0
BLACK = 1
WHITE = 2

# An Exception that is raised every time an invalid move occurs
class InvalidMoveException(Exception):
    ''' Raised whenever an exception arises from an invalid move '''
    pass


# The Othello class that manages the game state
class OthelloGameState:
    '''
    Class that creates the Othello game and deals with all its game logic
    '''
    
    # Initialize the game through the __init__() function.
    def __init__(self):
        ''' Creates the initial game state. '''
        self.current_board = np.zeros((8, 8), dtype=np.int8)
        self.current_board[3, 3] = WHITE
        self.currentsys.exc_info()[0]_board[3, 4] = BLACK
        self.current_board[4, 3] = BLACK
        self.current_board[4, 4] = WHITE
        self.frontier = {(2,2),(2,3),(2,4),(2,5),
                         (3,2),(3,5),(4,2),(4,5),
                         (5,2),(5,3),(5,4),(5,5)}
        self.turn = BLACK


    # This is the meat of the game logic. I define making a move through the
    # move() function, and within it are broken down helper functions that
    # make the code more reusable and the move() function more readable.
    def move(self, row: int, col: int) -> None:
        ''' Attempts to make a move at given row/col position.
            Current player/turn is the one that makes the move.
            If the player cannot make a move it raises an exception.
            If the player can make a move, the player finally plays
            the valid move and switches turn. '''
        
        # Check to see if the move is in a valid empty space
        # within the board's boundary
        if (row, col) not in self.frontier:
            raise InvalidMoveException
        
        # Retrieve a list of possible directions in which a valid move can occur.
        # (looks up to all 8 possible directions surrounding the move/cell)
        # The list only contains the directions where the opposite cell's color is
        # adjacent / touching the current cell. So it's not definite that the entire
        # list will return directions in which the cells in line of direction can be flipped.
        possible_directions = self._adjacent_opposite_color_directions(row, col, self.turn)
        
        # After having the list of possible directions, we begin keeping track of when a possible
        # valid move in a direction has been completed. The variable "next_turn" is used at the end
        # of this function to determine if the player switches turn, which only occurs if the
        # move is valid.
        #
        # The for loop looks through all of the possible directions, and if a direction is capable
        # of making a valid move/flip, then proceed into flipping the cells in that line of direction
        # and assign "next_turn" to the opposite turn to switch turns at the very end
        next_turn = self.turn
        for direction in possible_directions:
            if self._is_valid_directional_move(row, col, direction[0], direction[1], self.turn):
                next_turn = self._opposite_turn(self.turn)
            self._convert_adjacent_cells_in_direction(row, col, direction[0], direction[1], self.turn)


        # Here we decide if we can finally place down the current move and whether or not
        # we can switch turns. We decide to switch turns if the current player has made a valid move
        # AND the opposite player must have the option to be able to move in at least one empty cell
        # space. If the opposite player can't move in at least one empty cell space after the current
        # player has gone, we do not switch turns and the current player goes again for the second
        # time in a row.
        #
        # Ultimately, if the move is not valid, then raise an InvalidMoveException()
        if next_turn != self.turn:
            self.current_board[row, col] = self.turn
            self._update_frontier(row, col)
            if self.can_move(next_turn):
                self.switch_turn()
        else:
            raise InvalidMoveException()

    def _update_frontier(self, row: int, col: int) -> None:
        '''Updates the frontier set of possible move locations after a move has been made'''
        for current_row in range(row-1, row+2):
            if not self._is_valid_row_number(current_row):
                continue
            for current_col in range(col-1, col+2):
                if not self._is_valid_col_number(current_col):
                    continue
                if self.current_board[current_row, current_col] == NONE:
                    self.frontier.add((current_row, current_col))
        self.frontier.remove((row, col))

    def _is_valid_directional_move(self, row: int, col: int, rowdelta: int, coldelta: int, turn: str) -> bool:
        ''' Given a move at specified row/col, checks in the given direction to see if
            a valid move can be made. Returns True if it can; False otherwise.
            Only supposed to be used in conjunction with _adjacent_opposite_color_directions()'''
        current_row = row + rowdelta
        current_col = col + coldelta

        last_cell_color = self._opposite_turn(turn)

        while True:
            # Immediately return false if the board reaches the end (b/c there's no blank
            # space for the cell to sandwich the other colored cell(s)
            if not self._is_valid_cell(current_row, current_col):
                break
            if self._cell_color(current_row, current_col) == NONE:
                break           
            if self._cell_color(current_row, current_col) == turn:
                last_cell_color = turn
                break

            current_row += rowdelta
            current_col += coldelta
            
        return last_cell_color == turn


    def _adjacent_opposite_color_directions(self, row: int, col: int, turn: str) -> [tuple]:
        ''' Looks up to a possible of 8 directions surrounding the given move. If any of the
            move's surrounding cells is the opposite color of the move itself, then record
            the direction it is in and store it in a list of tuples [(rowdelta, coldelta)].
            Return the list of the directions at the end. '''
        dir_list = []
        for rowdelta in range(-1, 2):
            if not self._is_valid_row_number(row+rowdelta):
                continue
            for coldelta in range(-1, 2):
                if not self._is_valid_col_number(col+coldelta):
                    continue
                if self.current_board[row + rowdelta, col + coldelta] == self._opposite_turn(turn):
                    dir_list.append((rowdelta, coldelta))
        return dir_list
           

    def _convert_adjacent_cells_in_direction(self, row: int, col: int,
                                             rowdelta: int, coldelta: int, turn: str) -> None:
        ''' If it can, converts all the adjacent/contiguous cells on a turn in
            a given direction until it finally reaches the specified cell's original color '''
        if self._is_valid_directional_move(row, col, rowdelta, coldelta, turn):
            current_row = row + rowdelta
            current_col = col + coldelta
            
            while self._cell_color(current_row, current_col) == self._opposite_turn(turn):
                self._flip_cell(current_row, current_col)
                current_row += rowdelta
                current_col += coldelta


    # Functions to be used to determine if the game is over and what do when it is:
    #
    # is_game_over()
    # can_move()
    # return_winner()
    #
    def is_game_over(self) -> bool:
        ''' Looks through every empty cell and determines if there are
            any valid moves left. If not, returns True; otherwise returns False '''
        return self.can_move(BLACK) == False and self.can_move(WHITE) == False


    def can_move(self, turn: str) -> bool:
        ''' Looks at the frontier of the board and checks to
            see if the specified player can move in any of the cells.
            Returns True if it can move; False otherwise. '''
        for (row, col) in self.frontier:
            for direction in self._adjacent_opposite_color_directions(row, col, turn):
                if self._is_valid_directional_move(row, col, direction[0], direction[1], turn):
                    return True
        return False

    def return_winner(self) -> str:
        ''' Returns the winner. ONLY to be called once the game is over.
            Returns None if the game is a TIE game.'''
        black_cells = self.get_total_cells(BLACK)
        white_cells = self.get_total_cells(WHITE)

        if black_cells == white_cells:
            return None

        if black_cells > white_cells:
            return BLACK
        else:
            return WHITE


    # Utility functions for implementing ai agents
    
    def get_possible_moves(self):
        possible_moves = []
        for (row, col) in self.frontier:
            for direction in self._adjacent_opposite_color_directions(row, col, self.turn):
                if self._is_valid_directional_move(row, col, direction[0], direction[1], self.turn):
                    possible_moves.append((row, col))
                    break
        return possible_moves

    # Basic functions that perform simple tasks, ranging from retrieving
    # specific game data and switching turns:
    #
    # switch_turn()
    # get_rows()
    # get_columns()
    # get_turn()
    # get_total_cells()
    #
    def switch_turn(self) -> None:
        ''' Switches the player's turn from the current one to
            the other. Only to be called if the current player
            cannot move at all. '''
        self.turn = self._opposite_turn(self.turn)

    def get_board(self) -> [[str]]:
        ''' Returns the current game's 2D board '''
        return self.current_board

    def get_rows(self) -> int:
        ''' Returns the number of rows the game currently has '''
        return 8

    def get_columns(self) -> int:
        ''' Returns the number of columns the game currently has '''
        return 8

    def get_turn(self) -> str:
        ''' Returns the current game's turn '''
        return self.turn

    def get_total_cells(self, turn: str) -> int:
        ''' Returns the total cell count of the specified colored player '''
        total = 0
        for row in range(8):
            for col in range(8):
                if self.current_board[row, col] == turn:
                    total += 1
        return total


    # The rest of the functions are private functions only to be used within this module
    def _flip_cell(self, row: int, col: int) -> None:
        ''' Flips the specified cell over to the other color '''
        self.current_board[row, col] = self._opposite_turn(self.current_board[row][col])


    def _cell_color(self, row: int, col: int) -> str:
        ''' Determines the color/player of the specified cell '''
        return self.current_board[row, col]
        

    def _opposite_turn(self, turn: str) -> str:
        ''' Returns the player of the opposite player '''
        return {BLACK: WHITE, WHITE: BLACK}[turn]

    def _is_valid_cell(self, row: int, col: int) -> bool:
        ''' Returns True if the given cell move position is invalid due to
            position (out of bounds) '''
        return self._is_valid_row_number(row) and self._is_valid_col_number(col)

    def _is_valid_row_number(self, row: int) -> bool:
        ''' Returns True if the given row number is valid; False otherwise '''
        return 0 <= row < 8

    def _is_valid_col_number(self, col: int) -> bool:
        ''' Returns True if the given col number is valid; False otherwise '''
        return 0 <= col < 8

    
