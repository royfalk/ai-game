from enum import Enum
from random import randrange
import time
from typing import List
from copy import deepcopy


def getGfxCharacter(value: int) -> str:
    if value == 0:
        return "_"
    elif value == 1:
        return u"\u03BF"
    elif value == 2:
        return u"\u00D7"
    #raise ValueError(f"getGfxCharacter: illegal value {value}")
    return ""


Rules = Enum('Rules', ['classic', 'simple'])
States = Enum('States', ['in_progress','victory','defeat','stalemate'])

class GameRules:
    rounds: int
    solutions: List[List[int]]
    
    def __init__(self,rules:Rules):
        if rules == Rules.classic:
            self.rounds = 9
            self.solutions = [[0,1,2],[3,4,5],[6,7,8],
                     [0,3,6],[1,4,7],[2,5,8],
                     [0,4,8],[2,4,6]]
        else:
            self.rounds = 4
            self.solutions = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]

    def evaluateGame(self, data:List[int], round:int, move:int) -> States:
        if self.rounds == 4:
            for solution in self.solutions:
                if data[solution[0]] > 0 and data[solution[0]] == data[solution[1]]:
                    if data[solution[0]] == 2:
                        return States.victory
                    else:
                        return States.defeat
            return States.in_progress
        
        else:
            for solution in self.solutions:
                if data[solution[0]] > 0 and data[solution[0]] == data[solution[1]] and data[solution[0]] == data[solution[2]]:
                    # x is marked with 2 and plays on odd rounds
                    if data[solution[0]] == move:
                        return States.defeat
                    else:
                        return States.victory
                
            if round == 9:
                return States.stalemate
            
        return States.in_progress



class Board:
    rules: GameRules
    index: int
    round: int
    move: int
    parent: int
    status: int # 0 in play, 1 wins, 2 loss, 3 stalemate
    value: int
    bestMove: int 
    data: List[int]
    children: List[int]

    def __init__(self, rules:GameRules, index: int, round: int, parent: int, data: List[int]) -> None:
        self.rules = rules
        self.index = index
        self.round = round
        self.move = 1 if round % 2 == 0 else 2
        self.parent = parent
        self.status = 0 # 0 for in progress, 1 for end
        self.data = data
        self.value = 0
        self.bestMove = -1
        self.children = []

    def createChild(self, newIndex: int):
        newBoard = deepcopy(self)
        newBoard.index = newIndex
        newBoard.parent = self.index
        newBoard.round = self.round + 1
        newBoard.move = 1 if newBoard.round % 2 == 0 else 2
        newBoard.value = 0
        newBoard.bestMove = -1
        newBoard.children = []
        return newBoard
    
    def updateStatus(self):
        state = self.rules.evaluateGame(self.data, self.round, self.move)
        if state == States.victory:
            self.status = 1
            self.value = 1 
        elif state == States.stalemate:
            self.status = 3
        elif  state == States.defeat:
            self.status = 1
            self.value = -1
       
        

    def playMove(self, square: int): 
        move = 1 if self.round % 2 == 0 else 2
        self.data[square] = move


    def print(self):
        string: str = ""
        for index, char in enumerate(self.data):
            string += getGfxCharacter(char)
            
            if self.rules.rounds == 9 and index % 3 == 2:
                string += "\n"
            elif self.rules.rounds == 4 and index % 2 == 1:
                string += "\n"
        print(string)


class Game:
    boards: List[Board] = []
    currentIndex = 0

    def __init__(self, rules:GameRules):
        round = 0
        data = [0] * rules.rounds
        board = Board(rules, self.currentIndex, round, -1, data)
        self.boards.append(board)

    def evaluateChild(self, parent:Board, child:Board):
        if parent.bestMove == -1:
            parent.bestMove = child.index
            parent.value = child.value * (-1)
            return

        value = 0 # default for stalemate
        if child.value == 1: # child wins. bad for parent
            value = -1
        elif child.value == -1: # child loses. good for parent
            value = 1
        
        if parent.value < value:
            parent.value = value
            parent.bestMove = child.index


    def playRecursively(self, currentBoard: Board):
        if currentBoard.status > 0:
            #print(f"End R:{currentBoard.round} I:{currentBoard.index} B:{currentBoard.bestMove} V:{currentBoard.value}")
            #currentBoard.print()
            return

        for position, square in enumerate(currentBoard.data):
            if square > 0:
                continue

            self.currentIndex += 1
            currentBoard.children.append(self.currentIndex)
            newBoard = currentBoard.createChild(self.currentIndex)
            newBoard.playMove(position)
            newBoard.updateStatus()
            self.boards.append(newBoard)
            
            self.playRecursively(newBoard)
            self.evaluateChild(currentBoard, newBoard)
        
        #print(f"{currentBoard.status == 1} R:{currentBoard.round} I:{currentBoard.index} B:{currentBoard.bestMove} V:{currentBoard.value} {len(currentBoard.data)}")
        #currentBoard.print()
        
    def playOptimalGame(self):
        board = self.boards[0]
        #board.print()

        while board.status == 0:    
            board = self.boards[board.bestMove]
            #board.print()
        board.print()
        print(f"Result: {board.status}")

    def playOptimalVsRandom(self) -> int:
        board = self.boards[0]
        player = 0
        while board.status == 0:
            if player == 0:
                board = self.boards[board.bestMove]
                player = 1
            else:
                randomChild = randrange(len(board.children))
                randomMove = board.children[randomChild]
                board = self.boards[randomMove]
                player = 0
        #board.print()
        #print(f"Result: {board.status}")
        return board.status


gameRules = GameRules(Rules.classic)
game = Game(gameRules)#, 4, initialBoard)
start = time.time()
game.playRecursively(game.boards[0])
end = time.time()
print(f"Mapped {len(game.boards)} boards in {round(end-start)} seconds")

# Results in a stalemate as expected
#print("Optimal Game")
#game.playOptimalGame()

print("Optimal vs. Random Game")
randomResults = [0,0,0,0]
for i in range(10):
    result = game.playOptimalVsRandom()
    randomResults[result] += 1
print(f"Game still in progress (???): {randomResults[0]}")    
print(f"Player 1 wins: {randomResults[1]}")
print(f"Player 2 wins: {randomResults[2]}")
print(f"Stalemate: {randomResults[3]}")