class user:
    def __init__(self, dm, isAdmin = False, canVote = True):
        self.dm = dm
        self.canVote = canVote
        self.isAdmin = isAdmin
        self.ballot = {}
        self.hasCastBallot = False