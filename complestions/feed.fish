set -l feed_commands add browse delete refresh remove_topic topic version

complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a add -d 'add a new topic'
complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a browse -d 'browse a topic'
complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a help -d 'help about any command'
complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a refresh -d 'refresh the database'
complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a remove-topic -d 'remove a topic'
complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a topic -d 'prints all topics'
complete -f -c feed -n "not __fish_seen_subcommand_from $feed_commands" -a version -d 'print version'