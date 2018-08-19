
class Start_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', steps=1, cooldown=5, timer=5):
        self.ctx = ctx
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer

class Choose_One_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', steps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'choose_one'
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.step_number = 1
        self.clue_text = ''
        self.icon_key_per_line = 3
        self.emoji = []
        #The emoji item MUST be either in the form of unicode i.e. '\U00002B05' or if it is a custom guild emoji, fetched from the discord utility : discord.utils.get(ctx.author.guild.emojis, name='<name as it appears in guild emoji list>')
        self.emoji_answer_key_text = []
        #Note that this is indexed starting at one to be consistent with ease-of-use for combinations.
        self.correct_item_in_list = 1
        self.timer = 5
        self.image = ''
        self.attachments = []
        self.url = ''

class Combination_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', steps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'combination'
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.timer_between_combo_clicks = 30   #In seconds
        self.step_number = 1
        self.clue_text = ''
        self.icon_key_per_line = 3
        #The emoji item MUST be either in the form of unicode i.e. '\U00002B05' or if it is a custom guild emoji, fetched from the discord utility : discord.utils.get(ctx.author.guild.emojis, name='<name as it appears in guild emoji list>')
        self.emoji = []
        self.emoji_answer_key_text = []
        #Note that this is indexed starting at one for ease of matching up with question text.
        self.correct_combination = []
        self.timer = 5
        self.image = ''
        self.attachments = []
        self.url = ''

class Text_Card_Settings:
    def __init__(self, ctx, gamename='Current Game', keyname='Current Key', steps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'text'
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.correct_answer_text =''
        self.step_number = 1
        self.clue_text = ''
        self.timer = 5
        self.image = ''
        self.attachments = []
        self.url = ''

class Get_In_Game_Card_Settings:
    def __init__(self, ctx, gamename='Current Game', keyname='Current Key', steps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'get_in_game'
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.step_number = 1
        self.clue_text = ''
        self.timer = 5
        self.attempts_before_text_input = 2
        self.image = ''
        self.attachments = []
        self.url = ''

class Earned_Key_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', steps=1, cooldown=5, timer=5):
        self.ctx = ctx
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.step_number = 1
        self.clue_text = 'Replace with the next hint'
        self.image = ''
        self.attachments = []
        self.url = ''