# -*- coding: utf-8 -*-

board_width = 19
black_cant_place = 2
white_cant_place = 3

def leave(message):
    print message
    exit()

def get_cant_place(player):
    return white_cant_place if player == -1 else black_cant_place

def get_ennemy(player):
    return player * -1

def get_number_piece_aligned(board, x_s, y_s, x_inc, y_inc, player):
    count_aligned = 0
    for i in range(1, 5):
        x_check = x_s + (x_inc * i)
        y_check = y_s + (y_inc * i)
        if x_check < board_width and x_check >= 0 and y_check < board_width and y_check >= 0:
            if board[y_check][x_check] != player:
                return count_aligned
            count_aligned += 1
        else:
            return count_aligned
    return count_aligned

def get_align_possibility(board, x_s, y_s, x_inc, y_inc, player, ennemy):
    #Considering that the board[y_s][x_s] is not an ennemy piece
    count = 1
    contain_player = board[y_s][x_s] == player

    return_value = lambda has_player, count: count if has_player else 0

    for i in range(1, 5):
        x_check = x_s + (x_inc * i)
        y_check = y_s + (y_inc * i)
        if x_check < board_width and x_check >= 0 and y_check < board_width and y_check >= 0:
            if board[y_check][x_check] == ennemy:
                return return_value(contain_player, count)
            elif board[y_check][x_check] == player or board[y_check][x_check] == 2 or board[y_check][x_check] == 3:
                contain_player = True
            count += 1
        else:
            return return_value(contain_player, count)
    return return_value(contain_player, count)
    #return count

def is_capture_possible(x_s, y_s, x_inc, y_inc, player, ennemy, board, last_is_player = True):
    try:
        possibilities = [player]
        if not last_is_player:
            possibilities = [0, 2, 3]
        if y_s + y_inc < 0 or y_s + (y_inc * 2) < 0 or y_s + (y_inc * 3) < 0 or \
            x_s + x_inc < 0 or x_s + (x_inc * 2) < 0 or x_s + (x_inc * 3) < 0:
                return False
        check = board[y_s + y_inc][x_s + x_inc] == ennemy and \
            board[y_s + (y_inc *2)][x_s + (x_inc * 2)] == ennemy and \
            board[y_s + (y_inc * 3)][x_s + (x_inc * 3)] in possibilities
        return check
    except IndexError:
        return False

#Place the piece and check for capture
def place_piece(board, y, x, player, do_not_modify = False):
    sides = {
        'L': {'y': 0, 'x': -1},
        'U': {'y': -1, 'x': 0},
        'D': {'y': 1, 'x': 0},
        'R': {'y': 0, 'x': 1},
        'UR': {'y': -1, 'x': 1},
        'DR': {'y': 1, 'x': 1},
        'UL': {'y': -1, 'x': -1},
        'DL': {'y':1, 'x': -1}
    }
  
    if do_not_modify == False:
        board[y][x] = player
    ennemy = get_ennemy(player)
    captured = []
    for s in sides.keys():
        if is_capture_possible(x, y, sides[s]['x'], sides[s]['y'], player, ennemy, board):
            if do_not_modify == False:
                board[y + sides[s]['y']][x + sides[s]['x']] = 0
                board[y + (sides[s]['y'] * 2)][x + (sides[s]['x'] * 2)] = 0
            captured.append((y + sides[s]['y'], x + sides[s]['x']))
            captured.append((y + (sides[s]['y'] * 2), x + (sides[s]['x'] * 2)))
    return captured

def check_victory(board, y, x, player):
    #Assume that board[y][x] is a `player` piece
    sides = {
        'L': {'y': 0, 'x': -1, 'nb_aligned': 0},
        'U': {'y': -1, 'x': 0, 'nb_aligned': 0},
        'D': {'y': 1, 'x': 0, 'nb_aligned': 0},
        'R': {'y': 0, 'x': 1, 'nb_aligned': 0},
        'UR': {'y': -1, 'x': 1, 'nb_aligned': 0},
        'DR': {'y': 1, 'x': 1, 'nb_aligned': 0},
        'UL': {'y': -1, 'x': -1, 'nb_aligned': 0},
        'DL': {'y':1, 'x': -1, 'nb_aligned': 0}
    }
    opposites = [['L', 'R'], ['U', 'D'], ['UR', 'DL'], ['UL', 'DR']]
    ennemy = get_ennemy(player)

    end_check_aligned = False
    for s in sides.keys():
        sides[s]['nb_aligned'] = get_number_piece_aligned(board, x, y, sides[s]['x'], sides[s]['y'], player)
        #Check if one of the aligned can be captured
        #If yes, reduce the number of piece aligned
        end_check_aligned = False
        for i in xrange(sides[s]['nb_aligned'] + 1):
            for s2 in sides.keys():
                calculate = True
                #To avoid checking capture on the same line   
                for op in opposites:
                    if s2 in op and s in op:
                        calculate = False
                        break
                if calculate:
                    y_tmp = y + (i * sides[s]['y']) - sides[s2]['y']
                    x_tmp = x + (i * sides[s]['x']) - sides[s2]['x']
                    if y_tmp < 0 or x_tmp < 0 or x_tmp >= board_width or y_tmp >= board_width:
                        continue
                    if board[y_tmp][x_tmp] == ennemy or board[y_tmp][x_tmp] == 0 or board[y_tmp][x_tmp] == get_cant_place(player):
                        last_is_player = True if board[y_tmp][x_tmp] == 0 or board[y_tmp][x_tmp] == get_cant_place(player) else False
                        if is_capture_possible(x_tmp, y_tmp, sides[s2]['x'], sides[s2]['y'], ennemy, player, board, last_is_player):
                            sides[s]['nb_aligned'] = i - 1
                            end_check_aligned = True
                            break
            if end_check_aligned:
                break

    for t in opposites:
        #`+1` in the operation for the board[x][y] piece who is a `player` piece
        if sides[t[0]]['nb_aligned'] + sides[t[1]]['nb_aligned'] + 1 >= 5:
            return True
    return False
