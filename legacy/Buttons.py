__author__ = 'Dendär'


def clicked_play_button(player, i, plicon, paicon):
    player.play_item()
    if player.status is "playing":
        i.playpauseButton.setIcon(paicon)
    elif player.status is "paused":
        i.playpauseButton.setIcon(plicon)
    elif player.status is "stopped":
        clicked_stop_button(player, i)


def clicked_stop_button(player, i, plicon):
    player.stop_item()
    i.playpauseButton.setIcon(plicon)