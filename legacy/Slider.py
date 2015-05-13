__author__ = 'liothe'


def pressed(player):
    if player.status is "playing":
        player.pause_item()
        return True
    else:
        return False


def released(player, pre_state):
    if pre_state is True:
        player.play_item()