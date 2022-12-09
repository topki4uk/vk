import json
import sys

def main():
    d = {}
    with open('names.txt', 'r', encoding='utf-8') as name:
        names = name.read().split('\n\n')

    for name in names:
        name = name.split()

        d[name[0]] = name[1]

    #print(d)

    with open('marked.json', 'w+') as f:
        json.dump(d, f)

if __name__ == '__main__':
    main()