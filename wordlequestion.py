#!C:\Python38\python.exe
import random

def main():
    with open('answers.txt') as f:
        answers = f.read().splitlines()
    rand = random.randrange(2315)
    print(answers[rand])


if __name__=="__main__":
    main()