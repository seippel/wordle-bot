# wordle-bot
wordle-bot is a command line python based program that will solve the daily Wordle puzzle (https://www.nytimes.com/games/wordle/index.html).  This algorithm solves all puzzles in five guesses or less with an average of 3.62 guesses.

## Quickstart
Typical usage would be: `wordle.py --solve` and input the words the bot first guess on the webpage.  Once the webpage score its guess, that information is relayed back to the bot (* for green letters, ! for yellow, and X for gray) 

![image](https://github.com/seippel/wordle-bot/assets/40277570/8eaebe27-31c1-4bea-9b03-c032a1e72029)


## Advanced Usage
* This program can generate a random word from the wordle answer list `wordle.py --question`
* To get the program to generate a random word from the wordle answer list and solve that word `wordle.py --question --solve`
* To get the program to solve all words in the answer list (this can take some time, but is useful for judging improvements to the algorithm) `wordle.py --allwords`.  A box showing cumulative stats is shown after each word is solved.
