#Blackjack CLI

import random
import time
import sys
from typing import List, Tuple

from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.text import Text

colorama_init()
console = Console()

# logic
def deck_of_card() -> List[str]:
    deck = []
    suits = ["hearts", "diamonds", "clubs", "spades"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    for suit in suits:
        for rank in ranks:
            deck.append(f"{rank} of {suit}")
    random.shuffle(deck)
    return deck

def deal_card(hand: List[str], deck: List[str]) -> str:
    card = deck.pop()
    hand.append(card)
    return card

def hand_val(hand: List[str]) -> int:
    total = 0
    for card in hand:
        rank = card.split(" ")[0]
        if rank in ["J", "Q", "K"]:
            total += 10
        elif rank == "A":
            total += 11
        else:
            total += int(rank)
    aces = sum(1 for c in hand if c.split(" ")[0] == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

SUIT_SYMBOL = {
    "hearts": "♥",
    "diamonds": "♦",
    "clubs": "♣",
    "spades": "♠",
}

SUIT_COLOR = {
    "hearts": "red",
    "diamonds": "red",
    "clubs": "white",
    "spades": "white",
}

def ascii_card(card: str, hidden: bool = False) -> List[str]:
    if hidden:
        return [
            "┌─────────┐",
            "│░░░░░░░░░│",
            "│░░░░░░░░░│",
            "│░░░░░░░░░│",
            "│░░░░░░░░░│",
            "│░░░░░░░░░│",
            "└─────────┘",
        ]
    rank, _, suit = card.partition(" of ")
    suit_sym = SUIT_SYMBOL.get(suit, "?")
    left = rank.ljust(2)
    right = rank.rjust(2)
    return [
        "┌─────────┐",
        f"│{left}       │",
        "│         │",
        f"│    {suit_sym}    │",
        "│         │",
        f"│       {right}│",
        "└─────────┘",
    ]

def render_hand(hand: List[str], hide_first: bool = False) -> Text:
    if not hand:
        return Text("(no cards)")
    arts = []
    for i, c in enumerate(hand):
        hidden = hide_first and i == 0
        arts.append(ascii_card(c, hidden=hidden))
    lines = ["" for _ in range(7)]
    for art in arts:
        for i, l in enumerate(art):
            lines[i] += l + "  "
    result = Text()
    for ln in lines:
        formatted = ln
        for s, sym in SUIT_SYMBOL.items():
            color = SUIT_COLOR[s]
            formatted = formatted.replace(sym, f"[{color}]{sym}[/{color}]")
        result.append(Text.from_markup(formatted + "\n"))
    return result


CHIP_DENOMS = [1000, 500, 100, 50, 25, 5, 1]
CHIP_COLORS = {
    1000: "bold magenta",
    500: "bold yellow",
    100: "bold green",
    50: "bold blue",
    25: "bold red",
    5: "white",
    1: "dim white",
}

def format_chips(amount: int) -> Table:
    pieces = {}
    remaining = amount
    for d in CHIP_DENOMS:
        pieces[d] = remaining // d
        remaining = remaining % d
    table = Table.grid(expand=False)
    table.add_column(justify="center")
    table.add_column(justify="left")
    for d in CHIP_DENOMS:
        color = CHIP_COLORS.get(d, "white")
        table.add_row(f"[{color}]◉[/] {d}", f"x {pieces[d]}")
    return table

def staking(balance: int) -> Tuple[int, int]:
    console.print(Panel.fit(f"Your balance: [bold green]£{balance}[/bold green]", title="Balance"))
    console.print(Panel.fit("Place your bet using chip denominations. Type the number (e.g. 50) or a total amount.", title="Betting"))
    console.print(format_chips(min(balance, 5000)))

    while True:
        try:
            bet_input = console.input("[bold cyan]Enter your stake (or type 'chips'): [/]")
            if bet_input.strip().lower() == "chips":
                console.print("Enter chip quantities. Press Enter for 0.")
                total = 0
                for d in CHIP_DENOMS:
                    q = console.input(f"How many [{CHIP_COLORS.get(d,'white')}]{d}[/] chips? ")
                    q = int(q) if q.strip() != "" else 0
                    total += q * d
                bet = total
            else:
                bet = int(bet_input)

            if bet <= 0:
                console.print("[red]Must be > 0[/red]")
            elif bet > balance:
                console.print("[red]Bet exceeds balance[/red]")
            else:
                balance -= bet
                console.print(f"Bet [bold green]£{bet}[/bold green] — new balance [bold]{balance}[/bold]")
                return bet, balance
        except ValueError:
            console.print("[red]Invalid stake[/red]")

def animate_deal(to_who: str, card: str):
    steps = [
        Align.center(Text("Dealing...", style="bold yellow")),
        Align.center(Text(f"-> {to_who}: {card}", style="bold cyan")),
    ]
    with Live(steps[0], refresh_per_second=8, transient=True) as live:
        time.sleep(0.25)
        live.update(steps[1])
        time.sleep(0.20)

def hit_stand(player_hand: List[str], dealer_hand: List[str], deck: List[str]) -> bool:
    still_playing = True
    while still_playing:
        console.clear()
        console.rule("[bold magenta]Your Turn[/bold magenta]")
   
        dealer_visible_value = hand_val([dealer_hand[1]])
        console.print(Panel(render_hand(dealer_hand, hide_first=True), title=f"Dealer (showing {dealer_visible_value})"))
        console.print(Panel(render_hand(player_hand), title=f"Player (Total: {hand_val(player_hand)})"))

        choice = console.input("[bold cyan]Hit or Stand? (h/s): [/]").strip().lower()
        if choice == "h":
            drawn = deal_card(player_hand, deck)
            animate_deal("Player", drawn)
            if hand_val(player_hand) > 21:
                console.print(Panel(render_hand(player_hand), title=f"Player (BUST: {hand_val(player_hand)})", style="red"))
                console.print("[bold red]Bust![/bold red]")
                time.sleep(1)
                return False
        elif choice == "s":
            return True
        else:
            console.print("[red]Enter h or s[/red]")

def dealer_turn(dealer_hand: List[str], deck: List[str]):
    console.clear()
    console.rule("[bold magenta]Dealer's Turn[/bold magenta]")
    console.print(Panel(render_hand(dealer_hand, hide_first=False), title=f"Dealer (Total: {hand_val(dealer_hand)})"))
    time.sleep(0.8)
    while hand_val(dealer_hand) < 17:
        drawn = deal_card(dealer_hand, deck)
        animate_deal("Dealer", drawn)
        console.print(Panel(render_hand(dealer_hand, hide_first=False), title=f"Dealer (Total: {hand_val(dealer_hand)})"))
        time.sleep(0.8)
    console.print(f"Dealer stands with {hand_val(dealer_hand)}.")
    time.sleep(0.8)


def compare(player_hand: List[str], dealer_hand: List[str]) -> str:
    p = hand_val(player_hand)
    d = hand_val(dealer_hand)
    console.rule("[bold magenta]Final Hands[/bold magenta]")
    console.print(Panel(render_hand(player_hand), title=f"Player ({p})"))
    console.print(Panel(render_hand(dealer_hand, hide_first=False), title=f"Dealer ({d})"))

    if p > 21:
        return "dealer"
    if d > 21:
        return "player"
    if p > d:
        return "player"
    if d > p:
        return "dealer"
    return "push"

# game loop
def main():
    balance = 5000
    keep_playing = True

    console.print(Panel(Text("Welcome to Monaghan's Gambling Meccah (MGM) Casino!", justify="center"), subtitle="Dealer stands on 17"))

    while keep_playing:
        bet, balance = staking(balance)

        deck = deck_of_card()
        player_hand = []
        dealer_hand = []

        for _ in range(2):
            c = deal_card(player_hand, deck)
            animate_deal("Player", c)
            time.sleep(0.12)
            c = deal_card(dealer_hand, deck)
            animate_deal("Dealer", c)
            time.sleep(0.12)

        player_in = hit_stand(player_hand, dealer_hand, deck)

        if player_in:
            dealer_turn(dealer_hand, deck)

        winner = compare(player_hand, dealer_hand)

        if winner == "player":
            console.print(Panel(Text("You win!", style="bold green")))
            balance += bet * 2
        elif winner == "dealer":
            console.print(Panel(Text("Dealer wins!", style="bold red")))
        else:
            console.print(Panel(Text("Push!", style="bold yellow")))
            balance += bet

        console.print(f"Balance: [bold green]£{balance}[/bold green]")

        if balance <= 0:
            console.print(Panel(Text("You're out of money — restart to play again.", style="bold red")))
            break

        again = console.input("Play again? (y/n): ").strip().lower()
        if again != "y":
            keep_playing = False

    console.print("\nThanks for playing!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Game interrupted.[/red]")

        sys.exit(0)

