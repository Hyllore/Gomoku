package main

import "C"

import (
	"io/ioutil"
	"math"
	"strconv"
)

const BOARD_WIDTH int8 = 19
const BOARD_WIDTH_1D int16 = 361

const FILE_INPUT string = "tab.txt"
const FILE_OUTPUT string = "tab_out.txt"

const MIN_INFINITE int = -1000000000000
const MAX_INFINITE int = 1000000000000

const INC_1D int16 = int16(1)

var NB_PROCESS_FOR_BOARD_1D = int16(math.Ceil(float64(BOARD_WIDTH_1D)/float64(INC_1D)))

const VICTORY_POINTS int = MAX_INFINITE - 1

const black_piece = 1
const black_cant_place int8 = 2

const white_piece = -1
const white_cant_place int8 = 3

//eg: opposites_map[SIDE_L] = SIDE_R
var opposites_map = []int8{SIDE_R, SIDE_L, SIDE_D, SIDE_U, SIDE_DL, SIDE_UR, SIDE_DR, SIDE_UL}

const SIDE_L int8 = 0
const SIDE_R int8 = 1
const SIDE_U int8 = 2
const SIDE_D int8 = 3
const SIDE_UR int8 = 4
const SIDE_DL int8 = 5
const SIDE_UL int8 = 6
const SIDE_DR int8 = 7

const NB_SIDES int8 = 8

var NEEDED_SIDES_EVALUATE = []int8{SIDE_D, SIDE_R, SIDE_UR, SIDE_DR}

const black_piece_idx int8 = 0
const white_piece_idx int8 = 1

var NEEDED_SIDES_EVALUATE_SIZE = int8(len(NEEDED_SIDES_EVALUATE))
var sides_1d = []int16{
	-1, //L
	1, //R
	-19, //U
	19, //D
	-18, //UR
	18, //DL
	-20, //UL
	20, //DR
}

func read_array_from_file() []int8 {
	data, err := ioutil.ReadFile(FILE_INPUT)
	if err != nil {
		return nil
	}

	//361 = 19 * 19 = BOARD_WIDTH * BOARD_WIDTH
	//But int8 overflow 361 > 127
	if len(data) != 361 {
		return nil
	}

	var i int16 = 0
	array := make([]int8, BOARD_WIDTH_1D)
	for i = 0 ; i < BOARD_WIDTH_1D ; i++ {
		array[i] = 0
	}

	for i := 0 ; i < len(data); i++ {
		if data[i] < 48 && data[i] > 52 {
			return nil
		}
		val := int8(data[i] - 48)
		if val == 4 {
			array[19 * (i / 19) + (i % 19)] = -1
		} else {
			array[19 * (i / 19) +  (i % 19)] = int8(data[i] - 48)
		}
	}
	return array
}

func write_result_to_file(values [2]int16) {
	bytes := []byte(strconv.Itoa(int(values[0])) + "," + strconv.Itoa(int(values[1])))
	err := ioutil.WriteFile(FILE_OUTPUT, bytes, 0644)
	if err != nil {
	}
}

func is_board_empty(board *[]int8) bool {
	var y int16 = 0

	for y  = 0; y < BOARD_WIDTH_1D; y++ {
		if (*board)[y] != 0 {
			return false
		}
	}
	return true
}

func get_ennemy(player int8) int8 {
	return player * -1
}

func get_cant_place(player int8) int8 {
	if player == white_piece {
		return white_cant_place
	}
	return black_cant_place
}

func can_player_place_piece(player int8, tile_value int8) bool {
	if tile_value == 0 {
		//Empty tile
		return true
	}
	if (player == white_piece && tile_value == white_cant_place) || (player == black_piece && tile_value == black_cant_place) || tile_value == white_piece || tile_value == black_piece {
		//Check if not in double three case
		return false
	}
	return true
}

func has_nearby_piece(board *[]int8, pos int16) bool {
	var k int8 = 0
	var orig_col int8 = int8(pos % 19)

	var new_pos int16 = 0
	for k = 0 ; k < NB_SIDES ; k++ {
		new_pos = pos + sides_1d[k]
		if ((k == SIDE_UR || k == SIDE_DR || k == SIDE_R) && int8(new_pos % 19) != orig_col + 1) ||
		((k == SIDE_UL || k == SIDE_DL || k == SIDE_L) && int8(new_pos % 19) != orig_col - 1) {
			continue
		}
		if new_pos >= 0 && new_pos < BOARD_WIDTH_1D {
			if (*board)[new_pos] == white_piece || (*board)[new_pos] == black_piece {
				return true
			}
		}
	}
	return false
}

func get_number_piece_aligned(board *[]int8, pos int16, inc int16, player int8) int8 {
	var count_aligned int8 = 0
	var i_check int16 = 0
	var i int16 = 1
	var orig_col int16 = pos % 19

	for i = 1; i < 5; i++ {
		i_check = pos + (inc * i)
		//Consecutive `if` because they need to be done in that order to avoid errors / useless checks
		if i_check >= BOARD_WIDTH_1D || i_check < 0 ||
		((inc == sides_1d[SIDE_UR] || inc == sides_1d[SIDE_DR] || inc == sides_1d[SIDE_R]) && i_check % 19 != orig_col + i) ||
		((inc == sides_1d[SIDE_UL] || inc == sides_1d[SIDE_DL] || inc == sides_1d[SIDE_L]) && i_check % 19 != orig_col - i) {
			return count_aligned
		} else if (*board)[i_check] != player {
			return count_aligned
		} else if is_capture_possible_from_one_side(board, i_check, player) {
			return count_aligned
		}
		count_aligned++
	}
	return count_aligned
}

func get_align_possibility_return_value(contain_player bool, count int8) int8 {
	if !contain_player {
		return 0
	}
	return count
}

func get_align_possibility(board *[]int8, pos int16, inc int16, player int8, ennemy int8) int8 {
	//Considering that the board[y_s][x_s] is not an ennemy piece
	var count int8 = 1
	var contain_player bool = (*board)[pos] == player
	var i_check int16 = 0
	var i int16 = 0
	var orig_col int16 = pos % 19

	for i = 1; i < 5; i++ {
		i_check = pos + (inc * i)
		if i_check < BOARD_WIDTH_1D && i_check >= 0 &&
		((inc == sides_1d[SIDE_UR] || inc == sides_1d[SIDE_DR] || inc == sides_1d[SIDE_R]) && i_check % 19 == orig_col + i) &&
		((inc == sides_1d[SIDE_UL] || inc == sides_1d[SIDE_DL] || inc == sides_1d[SIDE_L]) && i_check % 19 == orig_col - i) {
			if (*board)[i_check] == ennemy {
				return get_align_possibility_return_value(contain_player, count)
			} else if (*board)[i_check] == player {
				contain_player = true
				if is_capture_possible_from_one_side(board, i_check,  player) {
					return get_align_possibility_return_value(contain_player, count)
				}
			}
			count++
		} else {
			return get_align_possibility_return_value(contain_player, count)
		}
	}
	return get_align_possibility_return_value(contain_player, count)
}

func non_player_capture_check(a int8) bool {
	if a == 0 || a == white_cant_place || a == black_cant_place {
		return true
	}
	return false
}

func is_capture_possible(board *[]int8, pos int16, inc int16, player int8, ennemy int8, last_is_player bool) bool {
	var orig_col int16 = pos % 19
	var pos1 int16 = pos + inc
	var pos2 int16 = pos + (inc * 2)
	var pos3 int16 = pos + (inc * 3)

	if pos1 < 0 || pos1 >= BOARD_WIDTH_1D || pos2 < 0 || pos2 >= BOARD_WIDTH_1D || pos3 < 0 || pos3 >= BOARD_WIDTH_1D {
		return false
	}
	if ((inc == sides_1d[SIDE_UR] || inc == sides_1d[SIDE_DR] || inc == sides_1d[SIDE_R]) &&
	((pos1 % 19 != orig_col + 1) || (pos2 % 19 != orig_col + 2) || (pos3 % 19 != orig_col + 3))) ||
	((inc == sides_1d[SIDE_UL] || inc == sides_1d[SIDE_DL] || inc == sides_1d[SIDE_L]) &&
	((pos1 % 19 != orig_col - 1) || (pos2 % 19 != orig_col - 2) || (pos3 % 19 != orig_col - 3))) {
		return false
	}
	return (*board)[pos1] == ennemy && (*board)[pos2] == ennemy && ((last_is_player && (*board)[pos3] == player) || (!last_is_player && non_player_capture_check((*board)[pos3])))
}
//TODO: Pas assez proteger des captures
func get_points_for_piece_placement(board *[]int8, player int8, pos int16, nb_captures int8) int {
	if check_victory(board, pos, player, true) {
		return VICTORY_POINTS
	}

	var pts int = 0
	var ennemy int8 = get_ennemy(player)

	var key int8 = 0

	var nb_aligned int8 = 0
	var nb_aligned_opp int8 = 0

	var nearby_ennemy int8 = 0
	var nearby_ennemy_opp int8 = 0

	var nb_row_max int8 = 0

	var inc int8 = 0

	var old_piece int8 = 0

	for inc = 0 ; inc < NEEDED_SIDES_EVALUATE_SIZE ; inc++ {
		key = NEEDED_SIDES_EVALUATE[inc]

		//----------------------------------------------------------------------------------
		nb_aligned = get_number_piece_aligned(board, pos, sides_1d[key], player) + 1
		nb_aligned_opp = get_number_piece_aligned(board, pos, -sides_1d[key], player)

		nearby_ennemy = get_number_piece_aligned(board, pos, sides_1d[key], ennemy)
		nearby_ennemy_opp = get_number_piece_aligned(board, pos, -sides_1d[key], ennemy)

		nb_row_max = get_align_possibility(board, pos, sides_1d[key], player, ennemy)
		//----------------------------------------------------------------------------------
		if nearby_ennemy + nearby_ennemy_opp >= 3 {
			//Blocked ennemy alignement
			pts += int(nearby_ennemy + nearby_ennemy_opp + 19)
		} else if nb_aligned == 3 || nb_aligned_opp == 2 {
			//Blocked capture
			pts += 19
		} else if nb_aligned + nb_aligned_opp >= 3 && nb_row_max >= 5 - nb_aligned_opp {
			//Alignement of 5 possible
			pts += int(nb_aligned + nb_aligned_opp)
		}
		if nb_aligned + nb_aligned_opp == 2 {
			pts -= 5
		}
		//----------------------------------------------------------------------------------
		//Check if a capture is done with this placement
		if is_capture_possible(board, pos, sides_1d[key], player, ennemy, true) {
			pts += 20
			nb_captures += 1
		} else if is_capture_possible(board, pos, sides_1d[key], player, ennemy, false) {
			//Check if a capture is possible when placing another piece
			pts += 15
		}
		//Opposite side
		if is_capture_possible(board, pos, -sides_1d[key], player, ennemy, true) {
			pts += 20
			nb_captures += 1
		} else if is_capture_possible(board, pos, -sides_1d[key], player, ennemy, false) {
			pts += 15
		}
		//----------------------------------------------------------------------------------
		//Check if this piece introduce a possible capture by the ennemy
		old_piece = (*board)[pos]
		(*board)[pos] = player
		if is_capture_possible_from_one_side(board, pos + sides_1d[key], player) {
			pts -= 19
		}
		//Opposite side
		if is_capture_possible_from_one_side(board, pos - sides_1d[key], player) {
			pts -= 19
		}
		(*board)[pos] = old_piece
		//----------------------------------------------------------------------------------

	}
	if nb_captures >=5 {
		return VICTORY_POINTS
	}
	return pts
}

func place_piece(board *[]int8, pos int16, captured *[]int16, nb_captures *[]int8, player int8, ennemy int8) {
	(*board)[pos] = player
	var nb_elems_captured int8 = 0
	var player_cap_idx int8 = get_idx_from_player(player)

	var k int8 = 0
	for k = 0 ; k < NB_SIDES ; k++ {
		if is_capture_possible(board, pos, sides_1d[k], player, ennemy, true) {
			(*board)[pos + sides_1d[k]] = 0
			(*board)[pos + (sides_1d[k] * 2)] = 0

			(*captured)[nb_elems_captured] = pos + sides_1d[k]
			(*captured)[nb_elems_captured + 1] = pos + (sides_1d[k] * 2)

			(*nb_captures)[player_cap_idx] += 1
			nb_elems_captured += 2
		}
	}
	if nb_elems_captured < 16 {
		(*captured)[nb_elems_captured] = -1
	}
}

func is_capture_possible_from_one_side(board *[]int8, pos int16, player int8) bool {
	var ennemy int8 = get_ennemy(player)
	var i_tmp int16 = 0
	var orig_col int8 = int8(pos % 19)

	var k int8 = 0
	for k = 0 ; k < NB_SIDES ; k++ {
		i_tmp = pos - sides_1d[k]
		//Reversed `orig_col + 1` and `orig_col - 1` because we made `pos - sides`
		if i_tmp < 0 || i_tmp >= BOARD_WIDTH_1D ||
		((k == SIDE_UR || k == SIDE_DR || k == SIDE_R) && int8(i_tmp % 19) != orig_col - 1) ||
		((k == SIDE_UL || k == SIDE_DL || k == SIDE_L) && int8(i_tmp % 19) != orig_col + 1) {
			continue
		}
		if (*board)[i_tmp] == ennemy || (*board)[i_tmp] == 0 || (*board)[i_tmp] == get_cant_place(player) {
			if is_capture_possible(board, i_tmp, sides_1d[k], ennemy, player, (*board)[i_tmp] != ennemy) {
				return true
			}
		}
	}
	return false
}

func check_victory(board *[]int8, pos int16, player int8, ignore_first bool) bool {
	if !ignore_first && (*board)[pos] != player {
		return false
	}

	var alignements = []int8{0, 0, 0, 0, 0, 0, 0, 0}

	var ennemy int8 = get_ennemy(player)
	var end_check_aligned bool = false

	var i int8 = 0
	var j int8 = 0

	var k int8 = 0
	var k2 int8 = 0

	var i_tmp int16 = 0

	var orig_col int8 = int8(pos % 19)

	for k = 0 ; k < NB_SIDES ; k += 2 {
		alignements[k] = get_number_piece_aligned(board, pos, sides_1d[k], player)
		alignements[k + 1] = get_number_piece_aligned(board, pos, sides_1d[k + 1], player)
		//Check a side and his opposite (as they are sorted that way in sides_1d)
		if alignements[k] + alignements[k + 1] + 1 >= 5 {
			//Check if one of the aligned can be captured
			//If yes, reduce the number of piece aligned
			//Check alignements[k + 0] and alignements[k + 1]
			for j = 0 ; j <= 1 ; j++ {
				end_check_aligned = false
				if alignements[k + j] == 0 {
					//Do not continue check if we have 0 piece aligned
					continue
				}
				//Check each piece of the alignement
				for i = 0; i <= alignements[k + j]; i++ {
					//Check each side of the piece we are on
					for k2 = 0 ; k2 < NB_SIDES ; k2++ {
						//Do not check capture at the beginning in the same direction as the alignement
						//Do not check capture at the end in the opposite direction as the alignement
						//Do not check capture in-between in the same or opposite direction as the alignement
						if (i == 0 && k2 != k + j) || (i == alignements[k + j] && opposites_map[k + j] != k2) || (i != 0 && i != alignements[k + j] && k + j != k2 && opposites_map[k + j] != k2) {
							i_tmp = pos + (sides_1d[k + j] * int16(i)) - sides_1d[k2]
							if i_tmp < 0 || i_tmp >= BOARD_WIDTH_1D {
								continue
							}
							if ((k + j == SIDE_UR || k + j == SIDE_DR || k + j == SIDE_R) &&
								(((k2 == SIDE_UR || k2 == SIDE_DR || k2 == SIDE_R) && int8(i_tmp % 19) != orig_col + 2) ||
								((k2 == SIDE_U || k2 == SIDE_D) && int8(i_tmp % 19) != orig_col + 1))) ||
							((k + j == SIDE_UL || k + j == SIDE_DL || k + j == SIDE_L) &&
								(((k2 == SIDE_UL || k2 == SIDE_DL || k2 == SIDE_L) && int8(i_tmp % 19) != orig_col - 2) ||
								((k2 == SIDE_U || k2 == SIDE_D) && int8(i_tmp % 19) != orig_col - 1))) {
								continue
							}

							if (*board)[i_tmp] == ennemy || (*board)[i_tmp] == 0 || (*board)[i_tmp] == get_cant_place(player) {
								if is_capture_possible(board, i_tmp, sides_1d[k2], ennemy, player, (*board)[i_tmp] != ennemy) {
									alignements[k + j] = i - 1
									end_check_aligned = true
									break
								}
							}
						}
					}
					if end_check_aligned {
						break
					}
				}
			}
			//Checking opposites
			if alignements[k] + alignements[k + 1] + 1 >= 5 {
				return true
			}
		}
	}
	return false
}

func max(a int, b int) int {
	if a > b {
		return a
	}
	return b
}

func min(a int, b int) int {
	if a > b {
		return b
	}
	return a
}

func get_nb_captured(captured []int16) int8{
	var i int8 = 0
	for i = 0 ; i < 16 ; i++ {
		if captured[i] == -1 {
			break
		}
	}
	return i / 2
}

func undo_move_and_capture(board *[]int8, pos int16, captured []int16, ennemy int8) {
	nb_elems := len(captured)
	for i := 0; i < nb_elems; i++ {
		if captured[i] == -1 {
			break
		}
		(*board)[captured[i]] = ennemy
	}
	(*board)[pos] = 0
}

func get_idx_from_player(player int8) int8 {
	if player == white_piece {
		return white_piece_idx
	}
	return black_piece_idx
}

func alphabeta_pruning(board *[]int8, points int, depth int8, alpha int, beta int, player int8, ennemy int8, nb_captures *[]int8, maximizing_player bool) int {
	if depth == 3 {
		return points
	}
	var tmp_points int = 0

	var v int = 0
	var i int16 = 0

	var captured = []int16{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1}
	if maximizing_player {
		v = MIN_INFINITE
	} else {
		v = MAX_INFINITE
	}

	var to_play int8 = player
	if !maximizing_player {
		to_play = ennemy
	}

	var player_idx int8 = get_idx_from_player(to_play)
	var tmp_nb_captures int8 = 0

	for i = 0 ; i < BOARD_WIDTH_1D ; i++ {
		if can_player_place_piece(to_play, (*board)[i]) && has_nearby_piece(board, i) {
			if maximizing_player {
				tmp_points = points + get_points_for_piece_placement(board, to_play, i, (*nb_captures)[player_idx])
			} else {
				tmp_points = points - get_points_for_piece_placement(board, to_play, i, (*nb_captures)[player_idx])
			}
			place_piece(board, i, &captured, nb_captures, to_play, to_play * -1)
			tmp_nb_captures = get_nb_captured(captured)

			if maximizing_player {
				v = max(v, alphabeta_pruning(board, tmp_points, depth + 1, alpha, beta, player, ennemy, nb_captures, !maximizing_player))
				alpha = max(alpha, v)
			} else {
				v = min(v, alphabeta_pruning(board, tmp_points, depth + 1, alpha, beta, player, ennemy, nb_captures, !maximizing_player))
				beta = min(beta, v)
			}

			undo_move_and_capture(board, i, captured, to_play * -1)
			(*nb_captures)[player_idx] -= tmp_nb_captures
			if beta <= alpha {
				return v
			}
		}
	}
	return v
}

func process_board(orig_board *[]int8, player int8, pos_s int16, pos_e int16, whites_captures int8, blacks_captures int8, channel_result chan<- [2]int) {
	var best_pos int16 = pos_s
	var best_val int = MIN_INFINITE

	var board = make([]int8, 361)
	copy(board, *orig_board)

	var captured = []int16{-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1}

	var val int = 0
	var tmp_points int = 0

	var ennemy int8 = get_ennemy(player)

	var nb_captures = []int8{blacks_captures, whites_captures}
	var player_idx int8 = get_idx_from_player(player)
	var tmp_nb_captures int8 = 0

	var i int16 = 0
	for i = pos_s ; i < pos_e ; i++ {
		if can_player_place_piece(player, board[i]) && has_nearby_piece(&board, i) {
			tmp_points = get_points_for_piece_placement(&board, player, i, nb_captures[player_idx])
			place_piece(&board, i, &captured, &nb_captures, player, ennemy)
			tmp_nb_captures = get_nb_captured(captured)

			if check_victory(&board, i, player, false) || nb_captures[player_idx] >= 5 {
				channel_result <- [2]int{VICTORY_POINTS, int(i)}
				return
			}
			val = alphabeta_pruning(&board, tmp_points, 0, MIN_INFINITE, MAX_INFINITE, player, player * -1, &nb_captures, false)

			undo_move_and_capture(&board, i, captured, player * -1)
			nb_captures[player_idx] -= tmp_nb_captures
			if val > best_val {
				best_pos = i
				best_val = val
			}
		}
	}
	channel_result <- [2]int{best_val, int(best_pos)}
}

//export Algorithm
func Algorithm(player int8, whites_captures int8, blacks_captures int8) {
	board := read_array_from_file()
	if board == nil {
		write_result_to_file([2]int16{-1, -1})
		return
	}
	if is_board_empty(&board) {
		write_result_to_file([2]int16{9, 9})
		return
	}

	var best_pos = [2]int16{0, 0}
	var best_val int = MIN_INFINITE

	results := make(chan [2]int, NB_PROCESS_FOR_BOARD_1D)

	var j int16 = 0
	var end_j int16 = 0

	for j = 0 ; j < BOARD_WIDTH_1D ; j += INC_1D {
		end_j = j + INC_1D
		if end_j > BOARD_WIDTH_1D {
			end_j = BOARD_WIDTH_1D
		}
		go process_board(&board, player, j, end_j, whites_captures, blacks_captures, results)
	}

	var i int16 = 0
	var y int16 = 0
	var x int16 = 0
	for i = 0; i < NB_PROCESS_FOR_BOARD_1D; i++ {
		elem := <-results
		y = int16(elem[1]) / int16(BOARD_WIDTH)
		x = int16(elem[1]) % int16(BOARD_WIDTH)
		if elem[0] == VICTORY_POINTS {
			write_result_to_file([2]int16{y, x})
			return
		} else if elem[0] > best_val {
			best_val = elem[0]
			best_pos[0] = y
			best_pos[1] = x
		}
	}
	write_result_to_file(best_pos)
}

func main() {}
