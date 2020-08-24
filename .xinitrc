#!/bin/sh
if [ -d /etc/X11/xinit/xinitrc.d ] ; then
    for f in /etc/X11/xinit/xinitrc.d/?* ; do
        [ -x "$f" ] && . "$f"
    done
    unset f
fi

#setxkbmap no
[[ -f ~/.Xresources ]] && xrdb ~/.Xresources
[[ -f ~/.Xmodmap ]] && xmodmap ~/.Xmodmap

[[ -d ~/bin ]] && export PATH=$PATH:$HOME/bin

hsetroot -solid "#000000"
compton --inactive-dim 0.2 --config /dev/null -b
#redshift -t 6500:3900 -b 1.0:0.8 -l 59.563499:10.067691 &
killall dunst
dunst -conf ~/.i3/dunstrc &
nm-applet &

export EDITOR="nvim"
export VISUAL="nvim"

xcape -e 'Control_L=Escape'
xcape -e 'Control_R=Escape'

exec i3
