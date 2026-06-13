class Currency:
    """Class that defines different currencies that help political parties byu votes."""
    def __init__(self, name, rate):
        self.name = name
        self.rate = rate

    def __eq__(self, other):
        return self.name == other.name and self.rate == other.rate
        

class PoliticalParty:
    """Class that defines political parties and currency-voters' conversion."""
    def __init__(self, name, motto, members=[], preferred_currency=None):
        self.name = name
        self.__motto = motto
        self.members = members
        self.preferred_currency = preferred_currency

    def convert_currency_to_voters(self, currency_count, currency):
        multiplier = 1
        if self.preferred_currency and currency == self.preferred_currency:
            multiplier *= 2
        
        return int(currency_count / currency.rate) * multiplier
    
    @property
    def motto(self):
        return self.__motto
    
    def __str__(self):
        return self.name

    def __add__(self, other):
        return Coalition(self, other)

class Coalition:
    """Class that defines coalitions and how they add parties."""
    def __init__(self, *parties):
        self.parties = list(parties)

    @property
    def members(self):
        return {party.name : party.members for party in self.parties}
        
    def __add__(self, other):
        new_parties = self.parties.copy()
        if isinstance(other, PoliticalParty):
            new_parties.append(other)
        elif isinstance(other, Coalition):
            new_parties.extend(other.parties)
        else:
            raise TypeError("Invalid type for Coalition.")
        
        return Coalition(*new_parties)
                         
    def __str__(self):
        return "-".join([party.name for party in self.parties])


class Elections:
    """Class that defines the election's process."""
    _history = {}

    def __init__(self, date):
        self.date = date
        self.participants = {}
        Elections._history[date] = self.participants

    def register_party_or_coalition(self, party_or_coalition):
        if not isinstance(party_or_coalition, (Coalition, PoliticalParty)):
            raise TypeError("Invalid type for Elections.")
        self.participants[party_or_coalition] = 0
        
    def vote(self, party_or_coalition):
        if party_or_coalition not in self.participants:
            # хубаво да се направи custom exception, but time is ticking away
            raise RuntimeError("Party or coalition not registered in the elections.")
        self.participants[party_or_coalition] += 1

    def rig_elections(self, party_or_coalition, count, currency):
        if isinstance(party_or_coalition, PoliticalParty):
            voters = party_or_coalition.convert_currency_to_voters(count, currency)
            self.participants[party_or_coalition] += voters
        elif isinstance(party_or_coalition, Coalition):
            max_voters = 0

            for party in party_or_coalition.parties:
                voters = party.convert_currency_to_voters(count, currency)
                if voters > max_voters:
                    max_voters = voters
            self.participants[party_or_coalition] += max_voters
        else:
            raise TypeError("Invalid type for rig_elections.")
        
    def get_results(self):
        return {str(party_or_coalition) : count for party_or_coalition, count in self.participants.items()}

    @staticmethod
    def get_results_by_year(year):
        if year in Elections._history:
            return {str(k): v for k, v in Elections._history[year].items()}
        return {}    
    