# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: grisbour <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2017/10/09 16:42:10 by grisbour          #+#    #+#              #
#    Updated: 2017/10/10 14:54:56 by grisbour         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = algo.so
SRC = algo.go
HEADERS = algo.h

all: $(NAME)

$(NAME):
	@go build -o $(NAME) -buildmode=c-shared $(SRC)

clean:
	@rm -rf utils.pyc graphic.pyc tab.txt tab_out.txt

fclean: clean
	@rm -rf $(NAME) $(HEADERS)

re: fclean all
