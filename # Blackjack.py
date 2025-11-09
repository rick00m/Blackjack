import random

def deck_of_card():
    deck = []
    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    for suit in suits:
        for rank in ranks:
            deck.append(f"{rank} of {suit}")
    random.shuffle(deck)
    return deck

def deal_card(hand, deck):
    card = deck.pop()
    hand.append(card)
    return card

def hand_val(hand):
    total = 0
    for card in hand:
        rank = card.split(" ")[0]
        if rank in ["J", "Q", "K"]:
            total += 10
        elif rank == "A":
            total += 11
        else:
            total += int(rank)
    while total > 21 and "A" in [c.split(" ")[0] for c in hand]:
        total -= 10
    return total

def staking(balance):
    print(f"\nYour balance is: £{balance}")
    while True:
        try:
            bet = int(input("Please enter your stake: "))
            if bet <= 0:
                print("Please enter a value greater than 0")
            elif bet > balance:
                print("Please lower your bet or make a deposit")
            else:
                balance -= bet
                print(f"£{bet} selected, your remaining balance is {balance}.")
                return bet, balance
        except ValueError:
            print("Please enter a valid stake")

def hit_stand(player_hand, dealer_hand, deck):
    still_playing = True
    while still_playing:
        print(f"\nYour hand: {', '.join(player_hand)} (Total: {hand_val(player_hand)})")
    
        print(f"Dealer shows: {dealer_hand[0]} (Value: {hand_val([dealer_hand[0]])})")

        choice = input("Hit or Stand? (h/s): ").strip().lower()
        if choice == "h":
            drawn_card = deal_card(player_hand, deck)
            print(f"You drew: {drawn_card}")
            if hand_val(player_hand) > 21:
                print(f"\nYour hand: {', '.join(player_hand)} (Total: {hand_val(player_hand)})")
                print("Bust! Game over.")
                return False
        elif choice == "s":
            print("You stand.")
            return True
        else:
            print("Please enter h or s.")

def dealer_turn(dealer_hand, deck):
    print("\nDealer's turn begins...")
    print(f"Dealer reveals full hand: {', '.join(dealer_hand)} (Total: {hand_val(dealer_hand)})")
    while hand_val(dealer_hand) < 17:
        drawn_card = deal_card(dealer_hand, deck)
        print(f"Dealer hits: {drawn_card}")
        print(f"Dealer's hand: {', '.join(dealer_hand)} (Total: {hand_val(dealer_hand)})")
    print(f"Dealer stands with: {', '.join(dealer_hand)} (Total: {hand_val(dealer_hand)})")

def compare(player_hand, dealer_hand):
    player_total = hand_val(player_hand)
    dealer_total = hand_val(dealer_hand)

    print(f"\nFinal Hands:")
    print(f"Your hand ({player_total}): {', '.join(player_hand)}")
    print(f"Dealer's hand ({dealer_total}): {', '.join(dealer_hand)}")

    if player_total > 21:
        return "dealer"
    elif dealer_total > 21:
        return "player"
    elif player_total > dealer_total:
        return "player"
    elif dealer_total > player_total:
        return "dealer"
    else:
        return "push"

balance = 5000
keep_playing = True

while keep_playing:

    bet, balance = staking(balance)

    deck = deck_of_card()
    player_hand = []
    dealer_hand = []

    for _ in range(2):
        deal_card(player_hand, deck)
        deal_card(dealer_hand, deck)

    player_in_game = hit_stand(player_hand, dealer_hand, deck)

    if player_in_game:
        dealer_turn(dealer_hand, deck)

    winner = compare(player_hand, dealer_hand)

    if winner == "player":
        print("You win!")
        balance += bet * 2
    elif winner == "dealer":
        print("Dealer wins!")
    else:
        print("Push!")
        balance += bet

    print(f"\nYour balance is now: £{balance}")

    again = input("\nPlay again? (y/n): ").lower()
    if again != "y":
        keep_playing = False

print("\nThanks for playing!")



    











        


    

