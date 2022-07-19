'''
# startgame (list_of_configurations):
- apply configuration 
- start round 
    - chose_catagory()
- loop until finished

return results_of_game # total points
'''
MAX_SPINS = 50

class ExecutiveLogic:
    def __init__(self):
        self.num_spins = 1
        self.round = 1
        pass

    def notifySpin(self):
        self.num_spins += 1
        return self.num_spins

    def getRound(self):
        return self.round

    def whoseTurn(self):
        return "Wil"

    def updateTurn(self):
        # return the next player
        return "Luis"

    def selectRandOpponent(self):
        return "Opponent"



