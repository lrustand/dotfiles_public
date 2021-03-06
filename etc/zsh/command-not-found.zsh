command_not_found_handler() {
  local pkgs cmd="$1"

  pkgs=(${(f)"$(pkgfile -b -v -- "$cmd" 2>/dev/null)"})
  if [[ -n "$pkgs" ]]; then
    printf '%s may be found in the following packages:\n' "$cmd"
    printf '  %s\n' $pkgs[@]
	echo -n "Replace? "
	while true; do
		read yn
		case $yn in
			[Yy]* ) echo "OK!"; break;;
			[Nn]* ) echo "Nop!"; break;;
			* ) echo "Please answer yes or no.";;
		esac
	done
    return 0
  fi

  printf 'zsh: command not found: %s\n' "$cmd" 1>&2
  return 127
}
