from . import models
from ._builtin import Page, WaitPage
from .models import Constants

def vars_for_all_templates(self):
	return {
			"round_number": self.round_number,
			"participant_id": self.player.id_in_group,
			"role": self.player.role
	}

class Introduction(Page):
	"""intro page with instructions, should show for all players"""
	# this should only be shown at the start
	def is_displayed(self):
		return self.round_number <= 1

class Prediction(Page):
	"""prediction page for potential amount receiver, should only show for receiver"""
	form_model = models.Group
	form_fields = ["predicted"]
	def vars_for_template(self):
		return {
			"other_player": models.ACTIVE_PLAYER_ID,
			"image_path": 'dictator_modified/img{}.jpg'.format(models.ACTIVE_PLAYER_ID)
		}
	def is_displayed(self):
		return self.player.role() == "receiver"

class Offer(Page):
	"""offer page for dictator to decide how much to share with receiver
	...should only be seen by active dictator"""
	form_model = models.Group
	form_fields = ["kept"]
	def is_displayed(self):
		# show only to active dictator
		return self.player.role() == "dictator" and self.player.is_active(models.ACTIVE_PLAYER_ID)

class WaitForOffer(WaitPage):
	def vars_for_template(self):
		return {
			"body_text": "Waiting for other player's offer"
		}
	def is_displayed(self):
		return self.player.role() == "receiver"

class Rating(Page):
	"""receiver rates fairness of offer"""
	form_model = models.Group
	form_fields = ["rating"]
	def offer(self):
		return Constants.endowment - self.group.kept
	def vars_for_template(self):
		return {
			'endowment': Constants.endowment,
			'offer': Constants.endowment - self.group.kept,
		}
	def is_displayed(self):
		return self.player.role() == "receiver"

class ToggleWaitPage(WaitPage):
	"""shown when ready to switch dictators - functionally, this is the end of the round"""
	def after_all_players_arrive(self):
		# set payoffs
		self.group.set_payoffs()
		# toggle activity status of player for different dictator next round:
		models.ACTIVE_PLAYER_ID = models.toggle_player_id( models.ACTIVE_PLAYER_ID )
	def vars_for_template(self):
		# get activity status of players from tracking dictionary in models:
		# generate message for wait screen during testing:
		inputs = (self.player.id_in_group, self.player.role()) 
				# self.player.is_active(models.ACTIVE_PLAYER_ID))
		body_text = """Thanks for your patience, participant {0}. Your role is still {1}.\n \n
				Waiting for the other 2 participants to end their turn.""".format(*inputs)
		# conditionally add a message about the dictator's sharing choice if they were active last round:
		if (self.player.role() == "dictator" and self.player.is_active(models.ACTIVE_PLAYER_ID)):
			choice_message = "You completed your turn. You shared {0} out of {1} with the receiver. \n \n".format(self.group.kept, Constants.endowment)
			body_text = choice_message + body_text
		return {"body_text": body_text}

class FinalPage(Page):
	"""def vars_for_template(self):
		return {
			'round_number': self.round_number,
		}"""
	def is_displayed(self):
		# this is shown at the end of the round
		return self.round_number >= Constants.num_rounds

page_sequence = [
	Introduction,
	Prediction,
	Offer,
	WaitForOffer,
	Rating,
	ToggleWaitPage,
	FinalPage,
]
