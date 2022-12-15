import math
from graphics import *
import random

class AbstractCell:
    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        self.id = id
        self.xpos = xpos
        self.ypos = ypos
        self.radius = radius
        self.color = color
        self.dx = dx
        self.dy = dy
        self.graphicsObj = Circle(Point(xpos, ypos), radius)

    def __str__(self):
        return  'coords: ' + self.xpos + ', ' + self.ypos + '\n'

    # Calculate how far the cell will move next turn
    # this is a temp function for testing, should be overwritten in children        
    def generateMove(self):
        # this is where we use an algorithm to decide where to move next
        return (self.dx, self.dy)

    def confirmMove(self, next_dx, next_dy):
        self.xpos += next_dx
        self.ypos += next_dy
        
    def getTravelDistance(self, cell, nextMove):
        # This needs to be modified when obstacles are added. 
        return math.sqrt((cell.xpos - (self.xpos + nextMove[0]))**2 + (cell.ypos - (self.ypos + nextMove[1]))**2)

    def hasCollided(self, otherCell):
        temp = 0


class Pathogen(AbstractCell):
    isTagged = False

    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        super().__init__(id, xpos, ypos, radius, color, dx, dy)

    def generateMove(self, healthyCells):
        right = (self.dx, 0)
        left = (-self.dx, 0)
        down = (0, self.dy)
        up  = (0, -self.dy) 
        nextMoves = [up, down, left, right]

        bestScore = float("inf")
        bestMove = up
        for cell in healthyCells:
            for move in nextMoves:
                travelDist = self.getTravelDistance(cell, move)
                #print("distance: ", travelDist)
                if travelDist < bestScore:
                    bestScore = travelDist
                    bestMove = move

        #print("best move: ", bestMove)
        return (bestMove[0], bestMove[1])

    
class HealthyCell(AbstractCell):   
    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        super().__init__(id, xpos, ypos, radius, color, dx, dy)

               
class THelper(AbstractCell):
    hasTagged = False #signals B cells and killer cells to indicate pathogen is near by

    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        super().__init__(id, xpos, ypos, radius, color, dx, dy)
        
    def isPathogenClose(self, pathogen):
        if self.getTravelDistance(pathogen, (0, 0)) <= 100:
            if self.getTravelDistance(pathogen, (0, 0)) <= self.radius + 15:
                self.hasTagged = True
                self.dx = pathogen.dx
                self.dy = pathogen.dy
                pathogen.isTagged = True
            return True
        else:
            self.hasTagged = False
            self.dx = 10
            self.dy = 10
            return False

    def generateMove(self, pathogens):
        right = (self.dx, 0)
        left = (-self.dx, 0)
        down = (0, self.dy)
        up  = (0, -self.dy) 
        nextMoves = [up, down, left, right]
        
        closestPathogen = pathogens[0]
        closestDistance = self.getTravelDistance(pathogens[0], (0, 0))
        for pathogen in pathogens[1:]:
            d = self.getTravelDistance(pathogen, (0, 0))
            if d < closestDistance:
                closestDistance = d
                closestPathogen = pathogen

        worstMove = right
        worstDistance = self.getTravelDistance(closestPathogen, right)
        for move in nextMoves[1:]:
            d = self.getTravelDistance(closestPathogen, move)
            if d > worstDistance:
                worstDistance = d
                worstMove = move
                        
        nextMoves.remove(worstMove)
                
        bestMove = nextMoves[random.randint(0, 2)]
        bestScore = float("inf")

        for pathogen in pathogens:
            if self.isPathogenClose(pathogen):
                for move in nextMoves:
                    travelDist = self.getTravelDistance(pathogen, move)
                    if travelDist < bestScore:
                        bestScore = travelDist
                        bestMove = move
                        
        return (bestMove[0], bestMove[1])


class TKiller(AbstractCell):

    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        super().__init__(id, xpos, ypos, radius, color, dx, dy)
        self.prevMov = (self.dx, 0)
        self.justCollided = False
        
    
    #need to do some kind of check to see if pathogen is close bc now just moving towards thelper cell
    def getTravelDistance(self, thelper, nextMove):
        return math.sqrt((thelper.xpos - (self.xpos + nextMove[0]))**2 + (thelper.ypos - (self.ypos + nextMove[1]))**2)
    
    #implement a generatemove that uses thelper signal cells  so it does not have information about pathogen itself 
    def generateMove(self, thelpers):
        right = (self.dx, 0)
        left = (-self.dx, 0)
        down = (0, self.dy)
        up  = (0, -self.dy) 
        nextMoves = [up, down, left, right]

        if self.justCollided:
            nextMoves.remove(self.prevMov)
            self.justCollided = False

        bestMove = (0, 0)
        bestScore = float("inf")
        for thelper in thelpers:
            if thelper.hasTagged == True:
                for move in nextMoves:
                    travelDist = self.getTravelDistance(thelper, move)
                    if travelDist < bestScore:
                        bestScore = travelDist
                        bestMove = move
                        self.prevMov = bestMove

        return (bestMove[0], bestMove[1])
        
    def hasCollided(self, otherCell):
        self.justCollided = True

class BCell(AbstractCell):
    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        super().__init__(id, xpos, ypos, radius, color, dx, dy)

class Antibodies(AbstractCell):
    def __init__(self, id, xpos, ypos, radius, color, dx, dy):
        super().__init__(id, xpos, ypos, radius, color, dx, dy)
        self.prevMov = (self.dx, 0)
        self.justCollided = False
        
    
    #need to do some kind of check to see if pathogen is close bc now just moving towards thelper cell
    def getTravelDistance(self, thelper, nextMove):
        return math.sqrt((thelper.xpos - (self.xpos + nextMove[0]))**2 + (thelper.ypos - (self.ypos + nextMove[1]))**2)
    
    #implement a generatemove that uses thelper signal cells  so it does not have information about pathogen itself 
    def generateMove(self, thelpers):
        right = (self.dx, 0)
        left = (-self.dx, 0)
        down = (0, self.dy)
        up  = (0, -self.dy) 
        nextMoves = [up, down, left, right]

        if self.justCollided:
            nextMoves.remove(self.prevMov)
            self.justCollided = False

        bestMove = (0, 0)
        bestScore = float("inf")
        for thelper in thelpers:
            if thelper.hasTagged == True:
                for move in nextMoves:
                    travelDist = self.getTravelDistance(thelper, move)
                    if travelDist < bestScore:
                        bestScore = travelDist
                        bestMove = move
                        self.prevMov = bestMove

        return (bestMove[0], bestMove[1])
        
    def hasCollided(self, otherCell):
        self.justCollided = True
