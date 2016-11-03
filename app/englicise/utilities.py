import random


def word_mask(word):
    retVal = ''
    for s in word.split(' '):
        if len(s) <= 5:
            num = 1
        elif len(s) <= 10:
            num = 2
        else:
            num = 3
        sample = random.sample(range(len(s)), num)
        for index, c in enumerate(s):
            if index in sample:
                retVal += r'\\' + c
            else:
                retVal += 'a'
        retVal += ' '
    return retVal.rstrip()


def word_strong(word, compareWord):
    retVal = ''
    for index, c in enumerate(word):
        if c == compareWord[index]:
            retVal += c
        else:
            retVal += "<strong class='bg-danger'>" + c + "</strong>"
    return retVal