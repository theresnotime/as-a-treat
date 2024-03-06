import random
from arrays import FOLX, TREATS

if __name__ == "__main__":
    status = f"{random.choice(FOLX)} can have {random.choice(TREATS)}, as a treat"
    print(status)
