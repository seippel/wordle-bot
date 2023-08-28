#!python3.8

import random, argparse, sys, requests
from datetime import datetime
from string import ascii_lowercase

answers = []
combined_list = []
current_guess = ""
guess_count = 0
questioner = False
solver = False
wordle = ""


def main():
    global guesses
    global answers
    global combined_list
    global current_guess
    global guess_count
    global questioner
    global solver
    letmeguess = False
    wordle = ""
    guess_count = 0
    loop_count = 1
    total_guesses = 0
    max_guesses = 0
    solve_distribution = {}
    
    #Verify command line arguments
    parser = argparse.ArgumentParser(description='Generate or solve Wordle puzzle.')
    parser.add_argument('--question', action='store_true', help="generate a wordle to solve")
    parser.add_argument('--solve', action='store_true', help="solve a wordle using the bot")
    parser.add_argument('--count', type=int, default=1, help="count for number of times bot should play itself")
    parser.add_argument('--letmeguess', action='store_true', help="Enter your own guesses and scores to see how many possible answers you have left")
    parser.add_argument('--allwords', action ='store_true', help="Have bot solve all words once (for stats).\r\n" +
                        "This option sets both --question and --solve.")
    args = parser.parse_args()
    loop_count = args.count
    if args.question:
        questioner = True
    if args.solve:
        solver = True
    if args.allwords:
        questioner = True
        solver = True
    if args.letmeguess:
        letmeguess = True
    if not questioner and not solver and not letmeguess:
        parser.print_help()
        parser.exit()
    with open('answers.txt') as f:
        all_wordle_list = f.read().splitlines()        
    all_wordle_list = append_answer_list(all_wordle_list)
    if args.allwords:
        loop_count = len(all_wordle_list)
    wordle_list = all_wordle_list.copy()
    answers = all_wordle_list.copy()
    if (questioner and not solver):
        wordle = generate_wordle(wordle_list)
        print(wordle)
        parser.exit()
    if letmeguess:
        letmeguessfunc()
        parser.exit()
    with open('guesses.txt') as f:
        guesses = f.read().splitlines()
    combined_list  = guesses+answers   #All valid answers we can make   
    for i in range(0, loop_count):
        print('\n*************New Game*************************\n')
        print('Starting game #', i)
        answers = all_wordle_list.copy()
        solution_found = False
        guess_count = 0
        if questioner:
            wordle = generate_wordle(wordle_list)
            wordle_list.remove(wordle)
        while not solution_found:
            print("current possible answers:", len(answers))
            if len(answers) <= 8:
                print('Possible answers:', answers)
            computer_guess = have_bot_guess_algo3(answers, combined_list)
            print('--------------------------')
            print("computer guess is: ", computer_guess)
            current_guess = computer_guess
            solution_found = guess(wordle, computer_guess)
        total_guesses = total_guesses + guess_count
        max_guesses = max(max_guesses, guess_count)
        if guess_count in solve_distribution:
            solve_distribution[guess_count] = solve_distribution[guess_count] + 1
        else:
            solve_distribution[guess_count] = 1
        print_stats(solve_distribution)
    print('solve_distribution: ', solve_distribution)
    print_stats(solve_distribution)
            

def append_answer_list(answer_list):
    #This is a temporary fix because NYT started adding answers not in the original answer list
    #Get todays date
    current_datetime = datetime.now()
    url = 'https://www.nytimes.com/svc/wordle/v2/' + format(current_datetime, '%Y') + '-' + format(current_datetime, '%m') + '-' + format(current_datetime, '%d') + '.json'
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    json_todays_answer = r.json()
    todays_answer = json_todays_answer['solution']
    if todays_answer not in answer_list:
        print()
        print('**************************************************************************')
        print('***** Note: Added todays answer the the list of possible solutions *******')
        print('**************************************************************************')
        answer_list.append(todays_answer)
        answer_list.sort()
    return answer_list

def generate_wordle(wordle_list):
    rand = random.randrange(len(wordle_list))
    wordle = wordle_list[rand]
    #wordle = 'antic'
    print('The wordle to guess is:', wordle)
    return wordle

def have_bot_guess_rand(answers, combined_list):
    #This algorithm solves the full answer bank with an average of 4.112 guesses (max varies - around 10ish)
    rand = random.randrange(len(answers))
    return answers[rand]

def have_bot_guess_algo1(answers, combined_list):
    #This algorithm guesses words based purely on the highest frequency of letters in the word
    #so if 'e' appear in the most possible remaining words, it will weight words with 'e' more heavily
    #This algorithm solves the full answer bank with an average of 3.97 guesses (max is 9)
    distribution = {}
    global guess_count
    #if guess_count == 0:
        #return 'rogue'   #4.04
        #return 'stair'  #3.93
        #return 'stare'  #3.87
        #return 'share'   #3.92
    if len(answers) < 3:
        #If we have only 1 or 2 possible answers, just answer or guess
        #rand = random.randrange(len(answers))
        #return answers[rand]
        return answers[0]   #Better not to make the guess random for stat purposes
    for answer in answers:
        for char_val in answer:
            if char_val in distribution:
                distribution[char_val] = distribution[char_val] + 1
            else:
                distribution[char_val] = 1
    print(distribution)
    #Score the possible guesses:
    best_guess = ""
    best_score = 0
    for possible_guess in combined_list:
        temp_distribution = distribution.copy()
        current_guess_score = 0
        for char_val in possible_guess:
            if char_val in temp_distribution:
                current_guess_score = current_guess_score + temp_distribution[char_val]
                #Remove it from dictionary so we don't overweight second/third occurances
                del temp_distribution[char_val]  
        if best_score < current_guess_score:
            best_guess = possible_guess
            best_score = current_guess_score
    return best_guess

def have_bot_guess_algo2(answers, combined_list):
    #This algorithm guesses words based with the smallest difference between 
    #So if there are 200 possible answer and 100 contain a 't', then 100 with 't' vs 100 without 't'
    #the algorithm would give that word a higher weight
    #This algorithm solves the full answer bank with an average of 3.76 guesses (max is 6)
    distribution = {}
    missingletterdistribution = {}
    global guess_count
    if len(answers) < 3:
        #If we have only 1 or 2 possible answers, just answer or guess
        #rand = random.randrange(len(answers))
        #return answers[rand]
        return answers[0]   #Better not to make the guess random for stat purposes
    for c in ascii_lowercase:
        for answer in answers:
            if c in answer:
                if c in distribution:
                    distribution[c] = distribution[c] + 1
                else:
                    distribution[c] = 1
                    if c not in missingletterdistribution:
                        missingletterdistribution[c] = 0
            else:
                if c in missingletterdistribution:
                    missingletterdistribution[c] = missingletterdistribution[c] + 1
                else:
                    missingletterdistribution[c] = 1
    #Score the possible guesses:
    best_guess = ""
    best_score = sys.maxsize * 2 + 1
    for possible_guess in combined_list:
        temp_distribution = distribution.copy()
        temp_missing_letter_distribution = missingletterdistribution.copy()
        current_guess_score = 0
        for char_val in possible_guess:
            if char_val in temp_distribution:
                current_guess_score = current_guess_score + abs(temp_distribution[char_val] - temp_missing_letter_distribution[char_val])
                #Remove it from dictionary so we don't overweight second/third occurances
                del temp_distribution[char_val]  
                del temp_missing_letter_distribution[char_val]
            else:
                #give max penalty score for second character
                current_guess_score = current_guess_score + len(answers)
        if best_score > current_guess_score:
            best_guess = possible_guess
            best_score = current_guess_score
    #If the score is the max possible score, all answers are anagrams of each other, ie: leapt, plate, pleat
    if best_score == len(answers) * 5:
        return answers[0]
    return best_guess

def have_bot_guess_algo3(answers, combined_list):
    #This algorithm groups goes through each possible guess and compares it to all possible wordle answers
    #It then determines what the maximum number of remaining answers would be given that guess (worst case)
    #This algorithm solves the full answer bank with an average of 3.62 guesses (max is 5)
    distribution = {}
    if len(answers) == 0:
        print('**************************************************************************************')
        print('* ERROR: Out of possible answers - check to be sure you entered the scores correctly *')
        print('**************************************************************************************')
        sys.exit(1)
    best_guess = answers[0]
    best_guess_max = len(answers)  #Worst case is all answers give the same score
    if guess_count == 0:
        #hard-coded to save time
        return 'aesir'   #3.62
        #=============================================
        #=  Total Puzzles solved:  2315              =
        #=  Average number of guesses: 3.62          =
        #=============================================
        #solve_distribution:  {3: 885, 4: 1252, 5: 118, 2: 60}
        #============Solved in========================
        #=  2 guesses:    60   *                     =
        #=  3 guesses:   885   *******               =
        #=  4 guesses:  1252   **********            =
        #=  5 guesses:   118   *                     =
        #=============================================
        #=  Total Puzzles solved:  2315              =
        #=  Average number of guesses: 3.62          =
        #=============================================
    if len(answers) < 3:
        #If we have only 1 or 2 possible answers, just guess the first one
        return answers[0]   #Better not to make the guess random for stat purposes
    for possible_guess in combined_list:
        for answer in answers:
            score_of_guess = score_guess(answer, possible_guess)
            if score_of_guess in distribution:
                distribution[score_of_guess] = distribution[score_of_guess] + 1
            else:
                distribution[score_of_guess] = 1
        #See how the word did
        guess_max = 0
        for key in distribution:
            if (guess_max < distribution[key]):
                guess_max = distribution[key]
        if guess_max < best_guess_max:
            best_guess = possible_guess
            best_guess_max = guess_max
        else:
            #If there is a tie between a word not in the possible answers and one in the answers
            #guess the one that could possibly be an answer
            if guess_max == best_guess_max and possible_guess in answers:
                best_guess = possible_guess
                best_guess_max = guess_max    
        distribution = {}
    return best_guess

def guess(wordle, computer_guess):
    global guess_count
    guess_count = guess_count + 1
    guesslen = 0
    print('We are on guess #', guess_count)
    valid = False
    guess_value = ""
    if questioner:  #if bot is playing itself
        guess_value = score_guess(wordle, computer_guess)
    else:
        while not valid:
            print('Score the guess in the format: X*! (X is complete miss, * is correct letter and spot, ! is correct letter, wrong spot)')
            guess_value = input()
            if len(guess_value) == 5 and (guess_value.count('X') + guess_value.count('*') + guess_value.count('!') == 5):
                valid = True
    if guess_value.count('*') == 5:
        print('Bot found the right answer in ', guess_count, ' guesses.')
        return True
    #Valid response, now prune the valid answer list
    prune_answers(guess_value)
    return False
        
def prune_answers(guess_value):
    #Guess value is something like *!XX!
    #current guess is the word the bot guessed
    remove_list = []
    if current_guess in answers:
        #We didn't exit, so current guess is wrong if it was an answer
        remove_list.append(current_guess)
    
    exact_dictionary = {}
    at_least_dictionary = {}
    for answer_index, answer_val in enumerate(answers):
        for guess_index, guess_val in enumerate(guess_value):
            #We know what this position is, see if it matches answer_val[guess_index]
            if guess_val == '*' and (current_guess[guess_index] != answer_val[guess_index]):
                #It wasn't a match, remove it
                if answer_val not in remove_list:
                    remove_list.append(answer_val)
            if guess_val == 'X' and (current_guess[guess_index] in answer_val):
                #Check if we have multiples of that letter in our guess_value
                if (current_guess.count(current_guess[guess_index]) == 1):
                    if answer_val not in remove_list:
                        remove_list.append(answer_val)
                else:
                    #Still remove it if all occurances got an X
                    all_instances_of_char = find(current_guess, current_guess[guess_index])
                    letter_count = 0
                    for i in all_instances_of_char:
                        if guess_value[i] != 'X':
                            letter_count = letter_count + 1
                    if letter_count == 0:
                        if answer_val not in remove_list:
                            remove_list.append(answer_val)
                    else:
                        #Remove any answers without exactly letter_count of this letter(current_guess[guess_index])
                        #This is really inefficient, needs to be improved
                        #Could store as a hashmap with letter as the key count as the value
                        #then just iterate through at the end of the loop
                        exact_dictionary[current_guess[guess_index]] = letter_count
            if guess_val == '!' and current_guess[guess_index] not in answer_val:
                if answer_val not in remove_list:
                    remove_list.append(answer_val)
                else:
                    #check how many times we guessed that letter
                    #If we guessed say 'chess' and both s characters
                    #came back as '!', we need to remove any word without at least 2 s characters
                    all_instances_of_char = find(current_guess, current_guess[guess_index])
                    letter_count = 0
                    for i in all_instances_of_char:
                        if guess_value[i] == '!' or guess_value[i] == '*':
                            letter_count = letter_count + 1
                    if letter_count == current_guess.count(current_guess[guess_index]):
                        #All occurrances of this letter scored as being in the answer (either * or !)
                        at_least_dictionary[current_guess[guess_index]] = letter_count
            if guess_val == '!' and (current_guess[guess_index] == answer_val[guess_index]):
                if answer_val not in remove_list:
                    remove_list.append(answer_val)
    for answer_index, answer_val in enumerate(answers):
        #Remove our edge cases stored in exact_dictionary and at_least_dictionary
        for key in exact_dictionary:
            if answer_val.count(key) != exact_dictionary[key]:
                if answer_val not in remove_list:
                    remove_list.append(answer_val)
        for key in at_least_dictionary:
            if answer_val.count(key) < at_least_dictionary[key]:
                if answer_val not in remove_list:
                    remove_list.append(answer_val)
    for wrong_word in remove_list:
        answers.remove(wrong_word)    

def letmeguessfunc():
    global current_guess
    attempt_count = 0
    while len(answers) > 1:
        print('-----------------------------------------')
        current_guess = ''
        guess_value = ''
        print('possible words remaining: ' + str(len(answers)))
        while len(current_guess) != 5:
            print('Enter the word you guessed')
            current_guess = input()
        while len(guess_value) != 5 or (guess_value.count('X') + guess_value.count('*') + guess_value.count('!') != 5):
            print()
            print('Score the guess in the format: X*! (X is complete miss, * is correct letter and spot, ! is correct letter, wrong spot)')
            guess_value = input()
        prune_answers(guess_value)
        attempt_count = attempt_count + 1
    print()
    if len(answers) == 0:
        print("You've eliminated all possible answers.  Check your input and try again.")
    else:
        print('Only one possible word remaining - You have used ' + str(attempt_count) + ' guesses to get to this point.')
    return
    
    
def score_guess(wordle, guess):
    response = '     '
    for i in range(0, 5):
        if wordle[i] == guess[i]:
            response = response[:i] + '*' + response[i+1:]
            guess = guess[:i] + ' ' + guess[i+1:]
            wordle = wordle[:i] + ' ' + wordle[i+1:]
    for i in range(0, 5):
        if response[i] == ' ':  #make sure we didn't already match here
            if guess[i] not in wordle:
                response = response[:i] + 'X' + response[i+1:]
            elif wordle.count(guess[i]) < guess.count(guess[i]):
                wordle_letter_count = wordle.count(guess[i])
                tempchar = guess[i]
                all_instances_of_char = find(guess, tempchar)
                for j in range(0, wordle_letter_count):
                    response = response[:all_instances_of_char[j]] + '!' + response[all_instances_of_char[j]+1:]
                for j in range(wordle_letter_count,len(all_instances_of_char)):
                    response = response[:all_instances_of_char[j]] + 'X' + response[all_instances_of_char[j]+1:]
            else:
                response = response[:i] + '!' + response[i+1:]
    return response

def print_stats(solve_distribution):
    total_puzzles = 0
    total_guesses = 0
    keys = []
    for key in solve_distribution:
        keys.append(key)
    keys.sort()
    max_distrib = 0
    for key in keys:
        max_distrib= max(max_distrib, solve_distribution[key])
    print('============Solved in========================')
    for key in keys:
        total_puzzles = total_puzzles + solve_distribution[key]
        total_guesses = total_guesses + solve_distribution[key] * key
        stars = round(solve_distribution[key] / max_distrib * 10)
        if stars == 0:
            stars = 1
        print('= ', key, 'guesses: ', '{:4d}'.format(solve_distribution[key]), '  ', end='')
        for i in range(0,stars):
            print('*', end='')
        for i in range(stars, 10):
            print(' ', end='')
        print('            =')
    print('=============================================')
    print('=  Total Puzzles solved:', '{:5d}'.format(total_puzzles), '             =')
    print('=  Average number of guesses:', '{:.2f}'.format(total_guesses/total_puzzles), '         =')
    print('=============================================')



def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]
    

if __name__=="__main__":
    main()
    