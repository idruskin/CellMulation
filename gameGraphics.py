import sys
from graphics import *


class GraphicsObject:
    def __init__(self, width, height):
        self.window = GraphWin("Cellmulation", width, height)
        self.agents = {}
        self.text = Text(Point(250, 100), "")
        self.addText("Welcome to the Cellmulation")

    def addAgent(self, agent):
        if not agent.id in self.agents.keys():
            self.agents[agent.id] = Circle(Point(agent.xpos, agent.ypos), agent.radius)
            self.updateAgent(agent, (0, 0))
            self.agents[agent.id].draw(self.window)

    def removeAgent(self, agent):
        if agent.id in self.agents.keys():
            self.agents[agent.id].undraw()
            del self.agents[agent.id]

    def addAgents(self, agentList):
        for agent in agentList:
            self.addAgent(agent)

    def updateAgent(self, agent, move):
        self.agents[agent.id].setFill(agent.color)
        self.agents[agent.id].move(move[0], move[1])

    def updateAgents(self, agentList, moves):
        for i in range(len(agentList)):
            self.updateAgent(agentList[i], moves[i])        

    def addText(self, message):
        self.text.setText(message)
        self.text.setFace('helvetica')
        self.text.setSize(16)
        self.text.setTextColor('black')
        self.text.draw(self.window)
    
    def changeText(self, message):
        self.text.setText(message)
