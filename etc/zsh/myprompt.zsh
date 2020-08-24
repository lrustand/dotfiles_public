setopt prompt_subst
autoload -Uz vcs_info
zstyle ':vcs_info:*' actionformats \
    '%F{5}(%f%s%F{5})%F{3}-%F{5}[%F{2}%b%F{3}|%F{1}%a%F{5}]%f '
zstyle ':vcs_info:*' formats '%b'
zstyle ':vcs_info:(sv[nk]|bzr):*' branchformat '%b%F{1}:%F{3}%r'

zstyle ':vcs_info:*' enable git cvs svn

vcs_info_wrapper() {
  vcs_info
  if [[ $(git status --porcelain 2>/dev/null) ]]; then
    changed=" %F{red}*%f"
  fi
  if [ -n "$vcs_info_msg_0_" ]; then
    echo " %F{2}[%b%F{green}${vcs_info_msg_0_}$changed%B%F{2}]"
  fi
}


export PROMPT=$'%(?..
%K{black}[%F{red}%?%f]%k)
%F{green}%B%K{black}[%T, %D{%d/%m/%y}]%f%k%b
%B%K{black}%F{%(!.red.green)}%n%f@%F{green}%m %F{grey}[$(shrink_path -l -t)]%f$(vcs_info_wrapper)%f%k%b
%K{black}%F{blue} %k
%K{black}%F{blue} -> %k%f'

#export RPROMPT='%K{black}[%F{%(?.lightgrey.red)}%?%f]%k'
