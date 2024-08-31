import random
class PokerGame:
    def __init__(self, player1_algorithm, player2_algorithm, starting_chips):
        self.player1 = player1_algorithm
        self.player2 = player2_algorithm
        self.starting_chips = starting_chips
        self.pot = 0
        self.current_bet = 0
        self.deck = list(range(2, 15))  # 2 to Ace (Ace is 14)
        self.initialize_game()

    def initialize_game(self):
        # Initialize player chips
        self.player1.chips = self.starting_chips
        self.player2.chips = self.starting_chips
        self.reset_game()

    def reset_game(self):
        self.pot = 0
        self.current_bet = 1  # Start with the big blind as the current bet
        self.deck = list(range(2, 15))  # Reset and shuffle deck
        random.shuffle(self.deck)
        self.player1.set_card(self.deck.pop())
        self.player2.set_card(self.deck.pop())

    def post_blinds(self):
        self.player1.chips -= 1  # Small blind
        self.player2.chips -= 2  # Big blind
        self.pot += 3  # Add blinds to the pot
        print(f"{self.player1.name} posts the small blind of 1 chip.")
        print(f"{self.player2.name} posts the big blind of 2 chips.")
        print(f"Pot is now {self.pot} chips.")

    def play_round(self):
        self.reset_game()
        self.post_blinds()  # Post blinds at the start of the round
        print(f"{self.player1.name} has {self.player1.card}")
        print(f"{self.player2.name} has {self.player2.card}")
        first = True
        current_player = self.player1
        opponent = self.player2
        last_bet = 2  # Big blind is the initial bet

        while True:
            # Current player makes a decision
            action, raise_amount = current_player.decide_action(opponent_card=opponent.card)
            print(f"{current_player.name} decides to {action}")

            if action == "fold":
                print(f"{current_player.name} folds. {opponent.name} wins the pot!")
                if opponent.card == 2:  # Special rule for winning with a 2
                    half_loser_chips = current_player.chips // 2
                    print(f"{opponent.name} wins with a 2! Taking half of {current_player.name}'s remaining chips: {half_loser_chips} chips.")
                    opponent.chips += half_loser_chips
                    current_player.chips -= half_loser_chips
                opponent.chips += self.pot
                return opponent

            if action == "call":
                call_amount = self.current_bet
                current_player.chips -= call_amount
                self.pot += call_amount
                print(f"{current_player.name} calls and puts {call_amount} chip(s) into the pot. Pot is now {self.pot} chips.")
                if not first:  # If both players have acted, end the betting round
                    print("Both players have called. Moving to showdown.")
                    break
                first = False

            if action == "raise":
                # Ensure the raise amount does not exceed the available chips of either player
                max_raise = min(raise_amount, current_player.chips, opponent.chips)
                current_player.chips -= max_raise
                self.pot += max_raise
                last_bet = max_raise
                self.current_bet = max_raise
                print(f"{current_player.name} raises and puts {max_raise} chips into the pot. Pot is now {self.pot} chips.")
                # Swap players for the next action
                current_player, opponent = opponent, current_player
                first = False
                continue  # The opponent now must act

            # Swap players for the next action
            current_player, opponent = opponent, current_player

        # Showdown
        winner = self.determine_winner()
        if winner:
            print(f"{winner.name} wins with a {winner.card} and takes the pot of {self.pot} chips!")
            winner.chips += self.pot

            if winner.card == 2:  # Special rule for winning with a 2
                loser = self.player1 if winner == self.player2 else self.player2
                half_loser_chips = loser.chips // 2
                print(f"{winner.name} wins with a 2! Taking half of {loser.name}'s remaining chips: {half_loser_chips} chips.")
                winner.chips += half_loser_chips
                loser.chips -= half_loser_chips

            return winner
        else:
            print("It's a tie!")
            return None

    def determine_winner(self):
        if self.player1.card > self.player2.card:
            return self.player1
        elif self.player2.card > self.player1.card:
            return self.player2
        else:
            return None

    def swap_blinds(self):
        # Swap the roles of the players for the next round
        self.player1, self.player2 = self.player2, self.player1

    def play_game(self):
        round_count = 1
        while self.player1.chips > 0 and self.player2.chips > 0:
            print(f"--- Round {round_count} ---")
            winner = self.play_round()
            print(f"{winner.name if winner else 'No one'} wins the round.")
            print(f"{self.player1.name} has {self.player1.chips} chips, {self.player2.name} has {self.player2.chips} chips")
            print("-" * 40)
            round_count += 1
            self.swap_blinds()  # Swap blinds after each round

        # Determine the overall winner
        if self.player1.chips <= 0:
            print(f"{self.player2.name} wins the game!")
        else:
            print(f"{self.player1.name} wins the game!")
