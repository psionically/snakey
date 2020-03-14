#This is a smart version of the classic snake arcade game using BFS
# to determine routes to take.


import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import random

#constant variables
HEAD = 0
FOOD = 0
LEFT = -1
RIGHT = 1
#bad move 
ERROR = -1111
#game board height
HEIGHT = 20
#game board width
WIDTH = 40
FIELD_SIZE = HEIGHT * WIDTH
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)
SNAKE = 2 * UNDEFINED
UP = -WIDTH
DOWN = WIDTH

#other variables
board = [0] * FIELD_SIZE
snake = [0] * (FIELD_SIZE+1)
snake[HEAD] = 1*WIDTH+1
snakeSize = 1
tempBoard = [0] * FIELD_SIZE
tempSnake = [0] * (FIELD_SIZE+1)
tempSnake[HEAD] = 1*WIDTH+1
tempSnakeSize = 1
level = 1
food = 3 * WIDTH + 3
bestMove = ERROR
dirs = [LEFT, RIGHT, UP, DOWN]
key = KEY_RIGHT                                                    

#function to check if a cell is free
def isFreeCell(index, sz, s):
    return not (index in s[:sz]) 

#function to check if a move is possible
def isPossibleMove(index, move):
    flag = False
    if move == LEFT:
        if index % WIDTH > 1:
            flag = True 
    elif move == RIGHT:
        if index % WIDTH < (WIDTH-2):
            flag = True
    elif move == DOWN:
        if index < (FIELD_SIZE-2*WIDTH):
            flag = True 
    elif move == UP:
        if index > (2*WIDTH-1):
            flag = True 
    return flag

#function to reset the board, sz = size
def resetBoard(s, sz, b):
    for i in xrange(FIELD_SIZE):
        if i == food:
            b[i] = FOOD
        elif isFreeCell(i, sz, s):
            b[i] = UNDEFINED
        else:
            b[i] = SNAKE

#function to refresh the board
def refreshBoard(f, s, b):
    queue = []

    queue.append(f)
    
    inqueue = [0] * FIELD_SIZE
    found = False


    while len(queue)!=0: 
        index = queue.pop(0)
        
        if inqueue[index] == 1:
            continue
        
        inqueue[index] = 1
        
        for i in xrange(4):
            if isPossibleMove(index, dirs[i]):
                if index + dirs[i] == s[HEAD]:
                    found = True
                    
                if b[index+dirs[i]] < SNAKE:
                    
                    if b[index+dirs[i]] > b[index]+1:
                        b[index+dirs[i]] = b[index] + 1
                        
                    if inqueue[index+dirs[i]] == 0:
                        queue.append(index+dirs[i])

    return found

#function to choose the shortest safe move
def shortestSafeMove(s, b):
    bestMove = ERROR
    min = SNAKE
    
    for i in xrange(4):
        if isPossibleMove(s[HEAD], dirs[i]) and b[s[HEAD] + dirs[i]] < min:
            min = b[s[HEAD] + dirs[i]]
            bestMove = dirs[i]
            
    return bestMove

#function to chose the longest safe move
def longestSafeMove(s, b):
    bestMove = ERROR
    max = -1
    
    for i in xrange(4):
        if isPossibleMove(s[HEAD], dirs[i]) and b[s[HEAD] + dirs[i]] < UNDEFINED and b[s[HEAD] + dirs[i]] > max:
            max = b[s[HEAD] + dirs[i]]
            bestMove = dirs[i]
            
    return bestMove

#function to check if the tail is inside
def tailInside():
    global tempBoard, tempSnake, food, tempSnakeSize
    tempBoard[tempSnake[tempSnakeSize-1]] = 0 
    tempBoard[food] = SNAKE
    
    result = refreshBoard(tempSnake[tempSnakeSize-1], tempSnake, tempBoard)
    
    for i in xrange(4): 
        if isPossibleMove(tempSnake[HEAD], dirs[i]) and tempSnake[HEAD] + dirs[i] == tempSnake[tempSnakeSize-1] and tempSnakeSize > 3:
            result = False
            
    return result

#function to follow the tail
def followTail():
    global tempBoard, tempSnake, food, tempSnakeSize
    tempSnakeSize = snakeSize
    tempSnake = snake[:]
    
    resetBoard(tempSnake, tempSnakeSize, tempBoard)
    
    tempBoard[tempSnake[tempSnakeSize-1]] = FOOD 
    tempBoard[food] = SNAKE
    
    refreshBoard(tempSnake[tempSnakeSize-1], tempSnake, tempBoard)
    
    tempBoard[tempSnake[tempSnakeSize-1]] = SNAKE 

    return longestSafeMove(tempSnake, tempBoard) 

#function for any possible move
def anyMove():
    global food , snake, snakeSize, board
    bestMove = ERROR
    
    resetBoard(snake, snakeSize, board)
    refreshBoard(food, snake, board)
    
    min = SNAKE

    for i in xrange(4):
        if isPossibleMove(snake[HEAD], dirs[i]) and board[snake[HEAD] + dirs[i]] < min:
            min = board[snake[HEAD] + dirs[i]]
            bestMove = dirs[i]
            
    return bestMove

#function to shift the array
def arrayShift(arr, size):
    for i in xrange(size, 0, -1):
        arr[i] = arr[i-1]

#function to place new food after snake eats the previous
def newFood():
    global food, snakeSize
    freeCell = False
    
    while not freeCell:
        w = random.randint(1, WIDTH-2)
        h = random.randint(1, HEIGHT-2)
        food = h * WIDTH + w
        freeCell = isFreeCell(food, snakeSize, snake)
   #paints food character to window     
    win.addch(food / WIDTH, food % WIDTH, 'o')

#function for the snake to choose a move
def makeMove(best):
    global key, snake, board, snakeSize, level
    
    arrayShift(snake, snakeSize)
    
    snake[HEAD] += best
    
    win.timeout(10)
    event = win.getch()
    
    if event == -1:
        key = key
    else:
        event 
    if key == 27:
        return

    h = snake[HEAD]
    #paints snake body character to screen
    win.addch(h / WIDTH, h % WIDTH, '.')

    
    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE
        snakeSize += 1
        level += 1
        
        if snakeSize < FIELD_SIZE:
            newFood()
    else:
        board[snake[HEAD]] = SNAKE 
        board[snake[snakeSize]] = UNDEFINED 
        win.addch(snake[snakeSize] / WIDTH, snake[snakeSize] % WIDTH, ' ')

#function for virtual shortest move
def virtShortestMove():
    global snake, board, snakeSize, tempSnake, tempBoard, tempSnakeSize, food
    tempSnakeSize = snakeSize
    tempSnake = snake[:] 
    tempBoard = board[:] 
    resetBoard(tempSnake, tempSnakeSize, tempBoard)
    
    eaten = False
    
    while not eaten:
        refreshBoard(food, tempSnake, tempBoard)
        
        move = shortestSafeMove(tempSnake, tempBoard)
        
        arrayShift(tempSnake, tempSnakeSize)
        
        tempSnake[HEAD] += move

        if tempSnake[HEAD] == food:
            tempSnakeSize += 1
            
            resetBoard(tempSnake, tempSnakeSize, tempBoard)
            
            tempBoard[food] = SNAKE
            eaten = True
        else:
            tempBoard[tempSnake[HEAD]] = SNAKE
            tempBoard[tempSnake[tempSnakeSize]] = UNDEFINED

#function to find a safe way
def safeWay():
    global snake, board
    safeMove = ERROR

    ShortestMove()
    
    if tailInside():
        return shortestSafeMove(snake, board)
    
    safeMove = followTail() 
    return safeMove

#terminal screen painting code, curses module
curses.initscr()
#win returns new window 
win = curses.newwin(HEIGHT, WIDTH, 0, 0)
#cursor is left where is it on update instead of being at cursor position
win.keypad(1)
#turns off echo mode (echoing of input characters)
curses.noecho()
#cursor state is set to invisible 
curses.curs_set(0)
#draws border around the window
win.border(0)
#if node is 1, getch() will be non-blocking
win.nodelay(1)
#paints the food character to window
win.addch(food / WIDTH, food % WIDTH, 'o')

#main loop that will terminate at level 600
#level 669 never finished - ran for over 2 hours
while level != 601:
    #terminal screen painting code, curses module
    #draws a border aroung the window
    win.border(0)
    #paints characters to the board
    win.addstr(0, 2, 'Level' + str(level) + ' ')
    #delay of 10
    win.timeout(10)

    event = win.getch()
    
    if event == -1:
        key = key
    else:
        event

    resetBoard(snake, snakeSize, board)
    

    if refreshBoard(food, snake, board):
        bestMove  = safeWay()
    else:
        bestMove = followTail()
            
    if bestMove == ERROR:
        bestMove = anyMove()
    
    if bestMove != ERROR: makeMove(bestMove)   
    else: break        

#will return to terminal when completed the game
#otherwise ctrl+c but will need to start new terminal
curses.endwin()

