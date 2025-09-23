import json

class GameState:
    """
    Represents the complete, mutable state of the game world.
    This object can be serialized and sent over the network to synchronize clients.
    """
    def __init__(self):
        self.variables = {}
        self.quests = {}
        self.skills = []
        self.inventory = []
        self.entities = {}
        self.items = {}
        self.lists = {}
        self.dictionaries = {}
        self.equipped_weapon = None
        self.equipped_shield = None
        self.equipped_armor = None
        self.equipped_cloak = None
        self.equipped_misc = []

    def to_json(self):
        """Serializes the game state to a JSON string."""
        return json.dumps({
            'variables': self.variables,
            'quests': self.quests,
            'skills': self.skills,
            'inventory': self.inventory,
            'entities': self.entities,
            'items': self.items,
            'lists': self.lists,
            'dictionaries': self.dictionaries,
            'equipped_weapon': self.equipped_weapon,
            'equipped_shield': self.equipped_shield,
            'equipped_armor': self.equipped_armor,
            'equipped_cloak': self.equipped_cloak,
            'equipped_misc': self.equipped_misc,
        }, indent=4)

    def from_json(self, json_string):
        """Deserializes a JSON string to update the game state."""
        data = json.loads(json_string)
        self.variables = data.get('variables', {})
        self.quests = data.get('quests', {})
        self.skills = data.get('skills', [])
        self.inventory = data.get('inventory', [])
        self.entities = data.get('entities', {})
        self.items = data.get('items', {})
        self.lists = data.get('lists', {})
        self.dictionaries = data.get('dictionaries', {})
        self.equipped_weapon = data.get('equipped_weapon')
        self.equipped_shield = data.get('equipped_shield')
        self.equipped_armor = data.get('equipped_armor')
        self.equipped_cloak = data.get('equipped_cloak')
        self.equipped_misc = data.get('equipped_misc', [])
