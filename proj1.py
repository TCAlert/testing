import random

pikaStats = {'hp': 100, 'acc' : 100}
bulbStats = {'hp': 100, 'acc' : 100}

def run():
  print("Goodbye!")
  return

def attackBulba(move):
  if move.lower() == 'tackle':
    print(f'Bulbasaur used {move.lower()}!')
    if random.random() * 100 < bulbStats['acc']:
      print('Bam!')
      pikaStats['hp'] = pikaStats['hp'] - 10
    else:
      print('But it missed!')
  elif move.lower() == 'sand attack':
    print(f'Bulbasaur used {move.lower()}!')
    if random.random() * 100 < bulbStats['acc']:
      print('Swoosh!')
      pikaStats['acc'] = pikaStats['acc'] - 10
    else:
      print('But it missed!')

def attackPika(move):
  num = 0
  if move.lower() == 'tackle':
    print(f'Pikachu used {move}!')
    if random.random() * 100 < pikaStats['acc']:
      print('Bam!')
      bulbStats['hp'] = bulbStats['hp'] - 10
    else:
      print('But t missed!')
  elif move.lower() == 'sand attack':
    print(f'Pikachu used {move}!')
    if random.random() * 100 < pikaStats['acc']:
      print('Swoosh!')
      bulbStats['acc'] = bulbStats['acc'] - 10
    else:
      print('But it missed!')
  elif move.lower() == 'catch':
    print('You caught a Bulbasaur!')
    if random.random() * 100 > (100 - bulbStats['hp']):
      print('But it broke free!')
    else:
      print('Congratulations!')
      num = 1
    
  return num

def bulbasaurMoves():
  if random.random() > 0.5:
    move = 'tackle'
  else:
    move = 'sand attack'
  attackBulba(move)

def pikachuMoves(choice):
  if choice == '1':
    move = 'tackle'
  elif choice == '2':
    move = 'sand attack'
  elif choice == '3':
    move = 'catch'
  else:
    move = 'invalid'
  end = attackPika(move)

  return move, end

def battle():
  print("Pikachu! I choose you!")

  while pikaStats['hp'] > 0 or bulbStats['hp'] > 0:
    print(f"Pikachu\n  HP: {pikaStats['hp']}  Acc: {pikaStats['acc']}")
    print(f"Bulbasaur\n  HP: {bulbStats['hp']}  Acc: {bulbStats['acc']}")

    bulbasaurMoves()
    if pikaStats['hp'] <= 0:
      print('You lost...')
      break    
    else:
      input("Press enter to continue\n")

    print('What to do?\n1. Tackle\n2. Sand Attack\n3. Throw Pokeball')
    try:
      i, end = pikachuMoves(input('<<Enter 1, 2, or 3>>'))
      if i == 'invalid':
        raise Exception('Invalid input.')
    except:
      while i.lower() == 'invalid':
        print('Your input was invalid. Try again.')
        i, end = pikachuMoves(input('<<Enter 1, 2, or 3>>'))

    if end == 1:
      print('You won!')
      input('What would you like to name your new Bulbasaur?\n')
      print('Nice name!')
      break
    else:
      input("Press enter to continue\n")

    if bulbStats['hp'] <= 0:
      print('The Bulbasaur fainted. You won!')
      break

  run()

def startGame():
  print("\nWhat do you want to do?\n1. Battle\n2. Run away!")
  choice = input()
  if choice.lower() == '1':
    battle()
  elif choice.lower() == '2':
    run()
  else:
    print('This is not a valid choice. Please try again.')
    startGame()

print("It's a Bulbasaur!")
input("Press enter to continue\n")
startGame()