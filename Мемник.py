from collections import defaultdict

memory = defaultdict(set)

def format_name(name):
    return name.replace("_", " ").title()

def memnick(*funcs):

    if not funcs:
        def decorator(func):
            def wrapper(*args, **kwargs):
                phrase = func(*args, **kwargs)
                target = format_name(phrase.split(",")[0].strip())
                speaker = format_name(func.__name__)
                memory[target].add((speaker, phrase))

                return phrase
            return wrapper
        return decorator

    result = []
    for func in funcs:
        target = format_name(func.__name__)
        print("TARGET:", target)
        for speaker, phrase in memory.get(target, []):
            result.append(f"С гласа на {speaker}: {phrase}")

    return result

@memnick()
def божана():
    return "Почекаин, ти си луд!"

божана()

@memnick()
def бай_венци():
    return "Емил, айде да играем шах!"

бай_венци()

@memnick()
def бай_венци():
    return "Емил, гладен съм!"

бай_венци()

@memnick()
def емил():
    return "Божана, намери сина ми."

емил()

@memnick()
def емил():
    return "Почекаин, нищо не става от тебе."

емил()

@memnick()
def почекаин():
    return "Божана, ще те любя."

почекаин()

print(memnick(почекаин))
print("MEMORY:", memory)
