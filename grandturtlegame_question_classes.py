class Join_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', steps = 1, api_key_required=True):
        self.ctx = ctx
        self.gamename = gamename
        self.steps = steps
        self.api_key_required = api_key_required
        self.image_url = ''
        self.prize_list=[]
        self.link_attachments=[]

class Finished_Game_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', steps = 1):
        self.ctx = ctx
        self.gamename = gamename
        self.steps = steps
        self.image_url = ''
        self.prize_list=[]
        self.link_attachments=[]

class Start_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', step_number=1, substeps=1, cooldown=5, timer=5):
        self.ctx = ctx
        self.gamename = gamename
        self.keyname = keyname
        self.step_number = step_number
        self.substeps = substeps
        self.cooldown = cooldown
        self.timer = timer
        self.description = True

class Choose_One_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', step_number=1, substep_number=1, substeps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'choose_one'
        self.gamename = gamename
        self.keyname = keyname
        self.step_number = step_number
        self.substep_number = substep_number
        self.substeps = substeps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.clue_text = ''
        self.icon_key_per_line = 3
        self.emoji = []
        #The emoji item MUST be either in the form of unicode i.e. '\U00002B05' or if it is a custom guild emoji, fetched from the discord utility : discord.utils.get(ctx.author.guild.emojis, name='<name as it appears in guild emoji list>')
        self.emoji_answer_key_text = []
        #Note that this is indexed starting at one to be consistent with ease-of-use for combinations.
        self.correct_item_in_list = 1
        self.image_url = ''
        self.file_attachments = []
        self.link_attachments = []
        self.url = ''

class Combination_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', step_number=1, substep_number=1, substeps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'combination'
        self.gamename = gamename
        self.keyname = keyname
        self.step_number = step_number
        self.substep_number = substep_number
        self.substeps = substeps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.timer_between_combo_clicks = 30   #In seconds
        self.clue_text = ''
        self.icon_key_per_line = 3
        #The emoji item MUST be either in the form of unicode i.e. '\U00002B05' or if it is a custom guild emoji, fetched from the discord utility : discord.utils.get(ctx.author.guild.emojis, name='<name as it appears in guild emoji list>')
        self.emoji = []
        self.emoji_answer_key_text = []
        #Note that this is indexed starting at one for ease of matching up with question text.
        self.correct_combination = []
        self.image_url = ''
        self.file_attachments = []
        self.link_attachments = []
        self.url = ''

class Text_Card_Settings:
    def __init__(self, ctx, gamename='Current Game', keyname='Current Key', step_number=1, substep_number=1, substeps=1, cooldown=5, timer=5, question_description = True):
        self.ctx = ctx
        self.card_type = 'text'
        self.gamename = gamename
        self.keyname = keyname
        self.step_number = step_number
        self.substep_number = substep_number
        self.substeps = substeps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.correct_answer_text =''
        self.clue_text = ''
        self.image_url = ''
        self.file_attachments = []
        self.link_attachments = []
        self.url = ''

class Get_In_Game_Card_Settings:
    def __init__(self, ctx, gamename='Current Game', keyname='Current Key', step_number=1, substep_number=1, substeps=1, cooldown=5, timer=10, question_description = True):
        self.ctx = ctx
        self.card_type = 'get_in_game'
        self.gamename = gamename
        self.keyname = keyname
        self.step_number = step_number
        self.substep_number = substep_number
        self.substeps = substeps
        self.cooldown = cooldown
        self.timer = timer
        self.question_description = question_description
        self.clue_text = ''
        self.item_id = ''
        self.required_amount = 1
        self.attempts_before_text_input = 2
        self.image_url = ''
        self.file_attachments = []
        self.link_attachments = []
        self.url = ''

class Earned_Key_Card_Settings:
    def __init__(self, ctx, gamename='Current Game Name', keyname='Current Key Name', step_number=1, substeps=1, cooldown=5, timer=5):
        self.ctx = ctx
        self.gamename = gamename
        self.keyname = keyname
        self.step_number = step_number
        self.substeps = substeps
        self.cooldown = cooldown
        self.timer = timer
        self.subsubstep_number = 1
        self.clue_text = 'Replace with the next hint'
        self.image_url = ''
        self.file_attachments = []
        self.link_attachments = []
        self.url = ''