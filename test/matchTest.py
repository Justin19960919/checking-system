from files import *
from match import Match


match = Match(CHECKING)
match.readCathay(FILE_CATHAY)
match.read711(FILE_711_1, FILE_711_2)
match.readPayPal(FILE_PAYPAL)

# Matching
match.matchCashFlow_cathay()
match.matchCashFlow_711()
match.matchCashFlow_paypal()


