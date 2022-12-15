import sys
import time, math
from gameGraphics import GraphicsObject
from cell import Pathogen, HealthyCell, THelper, TKiller, BCell, Antibodies
import argparse
import random

# Global varibles
FPS = 24
frameTime = 0
lastFrameTime = 0

numHealthy = 1
numPathogens = 1
numThelper = 1
numTkiller = 1
numBCell = 1
numDead = 0

screenSize = 1000

healthyRadius = 12
pathogenRadius = 15
thelperRadius = 11
tkillerRadius = 11
bcellRadius = 11
antibodyRadius = 4

healthySpeed = 0
pathogenSpeed = 3
thelperSpeed = 10 # TODO: Settle on a good tHelper speed
tkillerSpeed = 5
antibodySpeed = 20 
#need to add universal counter that tracks num of healthy cells and pathogens

def calculateDistance(xpos1, ypos1, xpos2, ypos2):
    return math.sqrt((xpos1 - xpos2)**2 + (ypos1 - ypos2)**2)

# returns distance between the centers of two cells
def calculateDist(cell1, cell2):
    return math.sqrt((cell1.xpos - cell2.xpos)**2 + (cell1.ypos - cell2.ypos)**2)

def generateDeadCell(toKill):
    toReturn = DeadCell('d%s' + str(numDead), toKill.xpos, toKill.ypos, toKill.radius, "GRAY", 0, 0)
    numDead += 1
    return toReturn

def updateAgentPositions(agents, moves):
    collisions = []
    num_agents = len(agents)
    for i in range(num_agents):
        for k in range(i + 1, num_agents):
            minDistance = agents[i].radius + agents[k].radius + .01
            distance = calculateDistance(agents[i].xpos + moves[i][0],
                                  agents[i].ypos + moves[i][1],
                                  agents[k].xpos + moves[k][0],
                                  agents[k].ypos + moves[k][1])
            if distance <= minDistance:
                collisions.append((agents[i], agents[k]))
                overlap = minDistance - distance

                xposDiff = (agents[i].xpos - agents[k].xpos)

                if xposDiff != 0:
                    theta = math.atan((agents[i].ypos - agents[k].ypos) / (agents[i].xpos - agents[k].xpos))
                else:
                    # for when theta is pi / 2 or -pi / 2
                    theta = (abs((agents[i].ypos - agents[k].ypos)) / ((agents[i].ypos - agents[k].ypos))) * math.pi / 2

                x_overlap = overlap * math.cos(theta)
                y_overlap = overlap * math.sin(theta)

                if moves[i][0] == 0 or moves[k][0] == 0:
                    if moves[i][0] == 0:
                        moves[k] = (moves[k][0] - x_overlap, moves[k][1])
                    elif moves[k][0] == 0:
                        moves[i] = (moves[i][0] - x_overlap, moves[i][1])
                else:
                    xratio = abs(moves[i][0]) / (abs(moves[i][0]) + abs(moves[k][0]))
                    moves[i] = (moves[i][0] - (xratio * x_overlap), moves[i][1])
                    moves[k] = (moves[k][0] - ((1 - xratio) * x_overlap), moves[k][1])

                if moves[i][1] == 0 or moves[k][1] == 0:
                    if moves[i][1] == 0:
                        moves[k] = (moves[k][0], moves[k][1] + y_overlap)
                    elif moves[k][1] == 0:
                        moves[i] = (moves[i][0], moves[i][1] + y_overlap)
                else:
                    yratio = abs(moves[i][1]) / (abs(moves[i][1]) + abs(moves[k][1]))
                    moves[i] = (moves[i][0], moves[i][1] + (yratio * y_overlap))
                    moves[k] = (moves[k][0], moves[k][1] + ((1 - yratio) * y_overlap))

    for i in range(num_agents):
        #sprint("confirmed move: ", (moves[i][0], moves[i][1]))
        agents[i].confirmMove(moves[i][0], moves[i][1])

    return collisions


def game(graphicsObj, healthyCells, pathogens, thelpers, tkillers, bcells, antibodies):
    antibodiesPresent = False
    allCells = healthyCells + pathogens + thelpers + tkillers + bcells
    graphicsObj.addAgents(allCells)

    lastFrameTime = time.time()
    gameOver = False

    while(not gameOver):
        frameTime = time.time()
        sleepAmt = 1./FPS - (frameTime - lastFrameTime)
        if sleepAmt > 0:
            time.sleep(sleepAmt)
        lastFrameTime = frameTime + sleepAmt
        # TODO: change variable names for better readability
        moves0 = []
        moves1 = []
        moves2 = []
        moves3 = []
        moves4 = []
        moves5 = []

        for healthy in healthyCells:
            moves0.append(healthy.generateMove())
        for pathogen in pathogens:
            moves1.append(pathogen.generateMove(healthyCells))
        for thelper in thelpers:
            moves2.append(thelper.generateMove(pathogens))
        for tkiller in tkillers:
            moves3.append(tkiller.generateMove(thelpers))
        for bcell in bcells:
            moves4.append(bcell.generateMove())
        for antibody in antibodies:
            moves5.append(antibody.generateMove(thelpers))
        if antibodiesPresent == True:
            moves = moves0 + moves1 + moves2 + moves3 + moves4 + moves5
        else:
            moves = moves0 + moves1 + moves2 + moves3 + moves4
        collisions = updateAgentPositions(allCells, moves)

        for collision in collisions:
            collision[0].hasCollided(collision[1])
            collision[1].hasCollided(collision[0])
            if isinstance(collision[0], Pathogen) and isinstance(collision[1], HealthyCell):
                collision[1].color = "GRAY"
                graphicsObj.updateAgent(collision[1], (0, 0))
                time.sleep(0.5)
                graphicsObj.removeAgent(collision[1])
                healthyCells.remove(collision[1])
            elif isinstance(collision[1], Pathogen) and isinstance(collision[0], HealthyCell):
                collision[0].color = "GRAY"
                graphicsObj.updateAgent(collision[0], (0, 0))
                time.sleep(0.5)
                graphicsObj.removeAgent(collision[0])
                healthyCells.remove(collision[0])
            elif isinstance(collision[0], TKiller) and isinstance(collision[1], Pathogen):
                graphicsObj.removeAgent(collision[1])
                pathogens.remove(collision[1])
            elif isinstance(collision[1], TKiller) and isinstance(collision[0], Pathogen):
                graphicsObj.removeAgent(collision[0])
                pathogens.remove(collision[0])
            elif isinstance(collision[0], THelper) and isinstance(collision[1], Pathogen):
                if antibodiesPresent == False:
                    antibodiesPresent = True
                    for bcell in bcells:
                        for i in range(4):
                            antibody = Antibodies('a%s' +str(i),random.randint(antibodyRadius, screenSize - antibodyRadius),random.randint(antibodyRadius, screenSize - antibodyRadius), 5, "YELLOW", antibodySpeed, antibodySpeed)
                            antibodies.append(antibody) 
                        for antibody in antibodies:
                            moves5.append(antibody.generateMove(thelpers))
                        graphicsObj.addAgents(antibodies)
                        graphicsObj.removeAgent(bcell)
                        bcells.remove(bcell)

            elif isinstance(collision[1], THelper) and isinstance(collision[0], Pathogen):
                if antibodiesPresent == False:
                    antibodiesPresent = True
                    for bcell in bcells:
                        for i in range(4):
                            antibody = Antibodies('a%s' +str(i),random.randint(antibodyRadius, screenSize - antibodyRadius),random.randint(antibodyRadius, screenSize - antibodyRadius), 5, "YELLOW", antibodySpeed, antibodySpeed)
                            antibodies.append(antibody) 
                        for antibody in antibodies:
                            moves5.append(antibody.generateMove(thelpers))
                        graphicsObj.addAgents(antibodies)
                        graphicsObj.removeAgent(bcell)
                        bcells.remove(bcell)
            elif isinstance(collision[0], Antibodies) and isinstance(collision[1], Pathogen):
                if collision[1] in pathogens:
                    graphicsObj.removeAgent(collision[1])
                    pathogens.remove(collision[1])
            elif isinstance(collision[1], Antibodies) and isinstance(collision[0], Pathogen):
                if collision[0] in pathogens:
                    graphicsObj.removeAgent(collision[0])
                    pathogens.remove(collision[0])
        
        if antibodiesPresent == True:
            allCells = healthyCells + pathogens + thelpers + tkillers + bcells + antibodies
            moves = moves0 + moves1 + moves2 + moves3 + moves4 + moves5
        else:
            allCells = healthyCells + pathogens + thelpers + tkillers + bcells
            moves = moves0 + moves1 + moves2 + moves3 + moves4
        graphicsObj.updateAgents(allCells, moves)

        gameOver = len(pathogens) == 0 or len(healthyCells) == 0

        gameStats = "Healthy cells: " +  str(len(healthyCells)) + " Pathogens: " +  str(len(pathogens))

        graphicsObj.changeText(gameStats)

    time.sleep(1)

    if len(pathogens) == 0:
        print("We killed all of the pathogens")
        graphicsObj.changeText("We killed all of the pathogens")
    if len(healthyCells) == 0:
        print("All of the healthy cells are dead")
        graphicsObj.changeText("All of the healthy cells are dead")

    time.sleep(3)


def main():

    healthyCells = []
    pathogenCells = []
    thelperCells = []
    tkillerCells = []
    bCells = []

    for i in range(numTkiller):
        tkiller = TKiller('k%s' + str(i), random.randint(tkillerRadius, screenSize - tkillerRadius),
                                     random.randint(tkillerRadius, screenSize - tkillerRadius),
                                     tkillerRadius, "BLACK", tkillerSpeed, tkillerSpeed)
        tkillerCells.append(tkiller)

    for i in range(numThelper):
        thelper = THelper('t%s' + str(i), random.randint(thelperRadius, screenSize - thelperRadius),
                                     random.randint(thelperRadius, screenSize - thelperRadius),
                                     thelperRadius, "GREEN", thelperSpeed, thelperSpeed)
        thelperCells.append(thelper)

    for i in range(numHealthy):
        healthy = HealthyCell('c%s' + str(i), random.randint(healthyRadius, screenSize - healthyRadius),
                                     random.randint(healthyRadius, screenSize - healthyRadius),
                                     healthyRadius, "BLUE", healthySpeed, healthySpeed)
        healthyCells.append(healthy)

    for i in range(numPathogens):
        pathogen = Pathogen('p%s' + str(i), random.randint(pathogenRadius, screenSize - pathogenRadius),
                                          random.randint(pathogenRadius, screenSize - pathogenRadius),
                                          pathogenRadius, "RED", pathogenSpeed, pathogenSpeed)
        pathogenCells.append(pathogen)

    for i in range(numBCell):
        bcell = BCell('b%s' + str(i), random.randint(bcellRadius, screenSize - bcellRadius),
                                     random.randint(bcellRadius, screenSize - bcellRadius),
                                     bcellRadius, "PURPLE", 0, 0)
        bCells.append(bcell)

    graphicsObj = GraphicsObject(screenSize, screenSize)

    game(graphicsObj, healthyCells, pathogenCells, thelperCells, tkillerCells, bCells, [])


if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("--healthy", help = "Number of healthy cells", default=1)
    parser.add_argument("--thelper", help = "Number of t helper cells", default=1)
    parser.add_argument("--tkiller", help = "Number of t killer cells", default=1)
    parser.add_argument("--pathogens", help = "Number of pathogens", default=1)
    parser.add_argument("--screensize", help = "Size of screen in pixels", default=500)


    # Read arguments from command line
    args = parser.parse_args()

    numHealthy = (int) (args.healthy)
    numThelper = (int)(args.thelper)
    numTkiller = (int)(args.tkiller)
    numPathogens = (int) (args.pathogens)
    screenSize = (int) (args.screensize)

    main()
