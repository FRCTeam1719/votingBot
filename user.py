class user:
    def __init__(self, dm, isAdmin = False, canVote = True):
        self.dm = dm
        self.canVote = canVote
        self.isAdmin = isAdmin
        self.ballot = {}
        self.hasVoted = False

    def __str__(self):
        return self.dm