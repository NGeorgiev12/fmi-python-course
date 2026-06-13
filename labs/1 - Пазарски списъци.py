costadines_requirements = (
    "вино",
    "презервативи",
    "струни за китара",
    "презервативи",
    "перце за китара",
    "презервативи",
    "пица",
    "бонбони",
    "презервативи"
)

victors_requirements = [
    "вино",
    "баница",
    "цяло пиле",
    "туршия",
    "кисело зеле",
    "зехтин",
    "картофи",
    "вино",
    "кисели краставички",
    "яйца"
]

joans_requirements = []
joans_requirements.extend(costadines_requirements)
joans_requirements.extend(victors_requirements)
joans_requirements.extend(["лубрикант", "хавлия", "маска на кон"])

unique_requirements = set(joans_requirements)
shopping_quantities = dict.fromkeys(unique_requirements, 5)
shopping_quantities["skyr"] = 5
total_items_to_buy = len(shopping_quantities)
