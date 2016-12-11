import random


def word_mask(word, seed=None, use_mask=True):
    retVal = ''
    for s in word.split(' '):
        if len(s) <= 5:
            num = 1
        elif len(s) <= 10:
            num = 2
        else:
            num = 3
        if seed:
            random.seed(seed)
        sample = random.sample(range(len(s)), num)
        for index, c in enumerate(s):
            if index in sample and use_mask:
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
            retVal += "<strong class='deep-orange lighten-4'>" + compareWord[index] + "</strong>"
    return retVal