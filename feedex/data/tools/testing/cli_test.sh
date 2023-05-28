#!/bin/bash
 


INSTR="0"
START_INSTR="$2"
if [[ "$START_INSTR" == "" ]]; then
    START_INSTR="0"
fi

export ONLY="$3"

F_Exec () {
    INSTR="$((INSTR+1))"
    [ "$INSTR" -le "$((START_INSTR-1))" ] && return

    ERR="F"
    ER=""
    COMM="$@"
    printf "\n\n========================================================================================\n"
    eval $@
    CODE=$?
    [ $CODE -ne 0 ] && ERR="T"
    printf "========================================================================================\n"
    printf "$COMM"
    [ "$ERR" == "T" ] && printf "      ERROR! ($CODE)    Instruction: $INSTR;    Continue? (y/n)\n"
    [ "$ERR" == "F" ] && printf "      OK!       Instruction: $INSTR;     Continue? (y/n)\n"

    [ "$ONLY" == "only" ] && exit 0
    read -n 1 CH
    [ "$CH" == "n" ] && exit 1

}
export -f F_Exec




# Display
if [[ "$1" == "docs" || "$1" == "all" ]]; then

    F_Exec /usr/bin/feedex --version
    F_Exec /usr/bin/feedex --about
    F_Exec /usr/bin/feedex -h
    F_Exec /usr/bin/feedex -hh

    F_Exec /usr/bin/feedex --help-feeds
    F_Exec /usr/bin/feedex --help-entries
    F_Exec /usr/bin/feedex --help-rules
    F_Exec /usr/bin/feedex --help-scripting
    F_Exec /usr/bin/feedex --help-examples
fi


if [[ "$1" == "db" || "$1" == "all" ]]; then
    # Test params and db edits

    F_Exec /usr/bin/feedex --debug --lock-fetching
    F_Exec /usr/bin/feedex --debug --db-stats
    F_Exec /usr/bin/feedex --debug --unlock-fetching

    TEST_DB="test.db"

    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --lock-db
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --unlock-db
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --db-stats
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --lock-db
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --db-stats
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --unlock-db

    export FEEDEX_DB_PATH="test2.DB"
    [ -f "$FEEDEX_DB_PATH" ] && rm -r "$FEEDEX_DB_PATH"

    F_Exec /usr/bin/feedex --debug --lock-db
    F_Exec /usr/bin/feedex --debug --db-stats
    F_Exec /usr/bin/feedex --debug --unlock-db

    F_Exec /usr/bin/feedex --debug --db-maintenance

    unset FEEDEX_DB_PATH

fi


if [[ "$1" == "config" || "$1" == "all" ]]; then

    TEST_CONFIG="test_config.conf"
    F_Exec /usr/bin/feedex --config="$TEST_CONFIG" --last_n=3 -q

fi




if [[ "$1" == "notify" || "$1" == "all" ]]; then

    F_Exec /usr/bin/feedex --last -q
    F_Exec /usr/bin/feedex --last_n=2 --group=category -q
    F_Exec /usr/bin/feedex --last --last_n=-2 -q
    F_Exec /usr/bin/feedex --last_n=sssssss -q
    F_Exec /usr/bin/feedex --last --group=flag --depth=3 -q
    F_Exec /usr/bin/feedex --headlines --group=category --depth=5 --last_n=3 -q
    F_Exec /usr/bin/feedex --short --group=feed --depth=5 --last_n=3 -q
    F_Exec /usr/bin/feedex --headlines --group=feed --depth=5 --last_n=3 -q

fi





if [[ "$1" == "basic_queries" || "$1" == "all" ]]; then
# Basic queries

    F_Exec /usr/bin/feedex -r 95093
    F_Exec /usr/bin/feedex -r 11
    F_Exec /usr/bin/feedex -L
    F_Exec /usr/bin/feedex --list-categories
    F_Exec /usr/bin/feedex --show-categories-tree
    F_Exec /usr/bin/feedex -F 1
    F_Exec /usr/bin/feedex -F 1111111
    F_Exec /usr/bin/feedex --examine-feed 1
    F_Exec /usr/bin/feedex --examine-feed 1111111111
    F_Exec /usr/bin/feedex --short -C Hilight
    F_Exec /usr/bin/feedex --csv -C Hilight
    F_Exec /usr/bin/feedex --json -C Hilight
    F_Exec /usr/bin/feedex --list-history
    F_Exec /usr/bin/feedex --list-rules
    F_Exec /usr/bin/feedex --list-flags
    F_Exec /usr/bin/feedex --feed=1 --flag=1 -q ''
    F_Exec /usr/bin/feedex --flag=all_flags --last_quarter -q ''
    F_Exec /usr/bin/feedex --flag="Tech" --last_quarter -q ''

    F_Exec /usr/bin/feedex --last --trends
    F_Exec /usr/bin/feedex --last --trending
    
fi


if [[ "$1" == 'queries' || "$1" == "all" ]]; then

    F_Exec /usr/bin/feedex --debug --last_quarter --plot --rel-in-time 109896
    F_Exec /usr/bin/feedex --debug --last_quarter --plot --rel-in-time 109896

    F_Exec /usr/bin/feedex --debug --feed=1 --last -q ''
    F_Exec /usr/bin/feedex --debug --feed=1 --last -q ''
    F_Exec /usr/bin/feedex --debug --feed=1 --last_week -q ""
    F_Exec /usr/bin/feedex --field=author --last_month -q "John"
    F_Exec /usr/bin/feedex --debug --field=publisher --last_month -q "Ars"

    F_Exec /usr/bin/feedex --debug --type=string --feed=1 --last -q ''
    F_Exec /usr/bin/feedex --type=string --debug --feed=1 --last -q ''
    F_Exec /usr/bin/feedex --type=string --debug --feed=1 --last_week -q ''
    F_Exec /usr/bin/feedex --type=string --field=author --last_month -q "John"
    F_Exec /usr/bin/feedex --type=string --debug --field=publisher --last_month -q "Ars"

    F_Exec /usr/bin/feedex --debug --type=full --feed=1 --last -q ''
    F_Exec /usr/bin/feedex --type=full --debug --feed=1 --last -q ''
    F_Exec /usr/bin/feedex --type=full --debug --feed=1 --last_week -q ''
    F_Exec /usr/bin/feedex --type=full --field=author --last_month -q "John"
    F_Exec /usr/bin/feedex --type=full --debug --field=publisher --last_month -q "Ars"
    F_Exec /usr/bin/feedex --type=full --field=title --last_month -q "Does"
    F_Exec /usr/bin/feedex --type=full --last_quarter -q "Vaccinations"

    F_Exec /usr/bin/feedex --debug --term-net "vaccine"
    F_Exec /usr/bin/feedex --debug --type=full --feed=1 --last_quarter --term-context "vaccine"
    F_Exec /usr/bin/feedex --debug --type=string --feed=1 --last_quarter --term-context "vaccine"
    F_Exec /usr/bin/feedex --debug --feed=1 --last_quarter --term-context "vaccine"

    F_Exec /usr/bin/feedex --debug --type=full --feed=1 --last_month --group=daily --term-in-time "vaccine"
    F_Exec /usr/bin/feedex --debug --type=full --feed=1 --last_month --group=daily --plot --term-in-time "Biden vaccine"


fi


if [[ "$1" == 'queries_wildcards' || "$1" == "all" ]]; then

    F_Exec /usr/bin/feedex --type=fts --case_ins --from='2021-01-01' --to='2021-06-01' -q "does"
    F_Exec /usr/bin/feedex --type=fts --case_ins --from='202ssssssss1-01-01' --to='2021-06-01' -q "Does"
    F_Exec /usr/bin/feedex --type=fts --case_ins --from='2021-01-01' --to='202aaaaaaaa1-06-01' -q "Does"

    F_Exec /usr/bin/feedex --type=fts --case_ins --last_month -q "Does"
    F_Exec /usr/bin/feedex --type=fts --case_sens --last_month -q "Does"
    F_Exec /usr/bin/feedex --type=string --case_ins --last_month -q "Does"
    F_Exec /usr/bin/feedex --type=string --case_sens --last_month -q "Does"
    
    F_Exec /usr/bin/feedex --debug --type=fts --feed=1 --last_quarter --term-context "'vaccine expected'"
    F_Exec /usr/bin/feedex --debug --type=string --feed=1 --last_quarter --term-context "'vaccine * expected'"
    F_Exec /usr/bin/feedex --debug --feed=1 --last_quarter --term-context "'vaccine Expected'"

    F_Exec /usr/bin/feedex --debug --type=full --feed=1 --last_month --group=daily --plot --term-in-time "'Vaccine expected'"
    F_Exec /usr/bin/feedex --debug --type=string --feed=1 --last_month --group=daily --plot --term-in-time "'vaccine * expected'"



fi

if [[ "$1" == 'queries_special' || "$1" == "all" ]]; then

    F_Exec /usr/bin/feedex --keywords 88157777777777
    F_Exec /usr/bin/feedex --keywords 88157
    F_Exec /usr/bin/feedex --rules-for-entry 88157777777777
    F_Exec /usr/bin/feedex --rules-for-entry 88157
    F_Exec /usr/bin/feedex --last_week -S 88157777777777
    F_Exec /usr/bin/feedex --debug --last_week -S 88157
    F_Exec /usr/bin/feedex -r 88157
    F_Exec /usr/bin/feedex --debug -r 88157

fi



# DB Actions
if [[ "$1" == 'actions_feed' || "$1" == "all" ]]; then
    TEST_DB="test.db"

    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-feed 1111111
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-feed 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --restore-feed 111111111
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --restore-feed 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 autoupdate 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 autoupdate 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 category Notes
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 category NONE
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 parent_category Hilight
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 parent_category NONE
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 error 5
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 error 0
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 link ad7t183gbklladbfkjahfskjhfash
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 autoupdate sssssss
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 parent_category Hilight
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 parent_category NONE
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 parent_id NONE
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 auth detect
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --debug -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --examine-feed 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --debug --examine-feed 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-feed 1 auth NONE
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --insert-feed-before 2 1


fi


if [[ "$1" == 'actions_category' || "$1" == "all" ]]; then
    TEST_DB="test.db"

    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-category "'test test'" "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --parent_category='Notes' --add-category "'test test'" "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-categories
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-category 111111111111111
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-category "'test test'"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-categories
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --restore-category "'test test'"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-categories
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-category 11111111 "title" "test111111"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-category "'test test'" "title" "test111111"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-categories
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -C "'test test'"

fi



if [[ "$1" == 'actions_rule' || "$1" == "all" ]]; then
    TEST_DB="test.db"

    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-keyword "''"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-keyword "test"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-rule 1 feed 2
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-rule 1 category Notes
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-rule 1 field desc
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-rule 1 field NONE
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --feed=1 --add-keyword "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --field=author --add-keyword "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --case_ins --feed=1 --add-keyword "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --case_sens --feed=1 --add-keyword "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-regex "''"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-regex "'[]..\.*aaaa\sd9(][\]][\]]'"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-regex "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-full-text "test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-rule 1 string 'gfgfgfgf'
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-rule 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --list-rules


fi


if [[ "$1" == 'actions_entry' || "$1" == "all" ]]; then
    TEST_DB="test.db"

    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex -r 881579999000000
    F_Exec /usr/bin/feedex -r 88157
    F_Exec /usr/bin/feedex --debug --mark 88157 0
    F_Exec /usr/bin/feedex --debug -o 88157
    F_Exec /usr/bin/feedex --debug --mark 88157 0
    F_Exec /usr/bin/feedex --debug --mark 88157 1
    F_Exec /usr/bin/feedex --debug --mark-unimportant 88157 1
    F_Exec /usr/bin/feedex --debug --flag 88157 2
    F_Exec /usr/bin/feedex --debug --flag 88157 0
    F_Exec /usr/bin/feedex --debug --flag 881579999999999 0
    F_Exec /usr/bin/feedex --debug --terms-for-entry 88157
    F_Exec /usr/bin/feedex --debug -o 881577777777
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --feed=1 --add-entry "test" "test test test"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -F 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --feed=1 --add-entry "test" "test test test"


fi



if [[ "$1" == 'actions_flag' || "$1" == "all" ]]; then

    TEST_DB="test.db"

    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --list-flags
    F_Exec /usr/bin/feedex --database="$TEST_DB" --add-flag "test" "test test"
    F_Exec /usr/bin/feedex --database="$TEST_DB" --edit-flag 1 "color_cli" "blue"
    F_Exec /usr/bin/feedex --database="$TEST_DB" --edit-flag 1 "color_cli" "RED"
    F_Exec /usr/bin/feedex --database="$TEST_DB" --list-flags
    F_Exec /usr/bin/feedex --database="$TEST_DB" --edit-flag 1 "id" 2
    F_Exec /usr/bin/feedex --database="$TEST_DB" --edit-flag 1 "id" 12
    F_Exec /usr/bin/feedex --database="$TEST_DB" --list-flags
    F_Exec /usr/bin/feedex --database="$TEST_DB" --delete-flag 2
    F_Exec /usr/bin/feedex --database="$TEST_DB" --list-flags


fi



if [[ "$1" == 'actions_entry_add' || "$1" == "all" ]]; then
    
    TEST_DB="test.db"
    IFILE="test_ifile.json"
    IFILE2="test_ifile2.json"
    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"


    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-entry "'Test'" "'DESC Test'"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --no-learn --add-entry "'Test'" "'DESC Test'"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --parent_category='Hilight' --add-entry "'Test'" "'DESC Test'"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --parent_category='Hilight' --no-learn --add-entry "'Test'" "'DESC Test'"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --feed=1 --add-entry "'Test'" "'DESC Test'" 
    F_Exec /usr/bin/feedex --database="$TEST_DB" -F 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-entry 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -F 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --restore-entry 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -F 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-entry 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-entry 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -F 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --delete-entry 199999999999
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --restore-entry 199999999999
 

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --parent_category='Notes' --add-entry "'Test'" "'DESC Test'" 
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --parent_category='Notes' --add-entry "'Test'" "'DESC Test'" 

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-entries-from-file "$IFILE"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-entries-from-file "$IFILE2"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --no-learn --add-entries-from-file "$IFILE"

    F_Exec /usr/bin/feedex --database="$TEST_DB" -F 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -C 'Notes'

    F_Exec /usr/bin/feedex --database="$TEST_DB" --keywords 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" --keywords 2

fi


if [[ "$1" == 'actions_entry_edit' || "$1" == "all" ]]; then

    TEST_DB="test.db"
    IFILE="test_ifile.json"
    IFILE2="test_ifile2.json"
    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --database="$TEST_DB" --add-entries-from-file "$IFILE"
    F_Exec /usr/bin/feedex --database="$TEST_DB" -F 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 text "'Testing editing asssssssss fdfdlfjirjirf fdkjfdkjfksd dsf;j;fkjrijsd;fj;l sd;flj;ljsdf'"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 text "'Testing editing asssssssss fdfdlfjirjirf fdkjfdkjfksd dsf;j;fkjrijsd;fj;l sd;flj;ljsdf'"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 read 5
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 read 0
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --keywords 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -r 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 flag 5
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 flag 0
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --keywords 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -r 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 feed_id 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 feed_id 2
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --keywords 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -r 1

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 parent_category Notes
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --edit-entry 1 feed_id 2
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --keywords 1
    F_Exec /usr/bin/feedex --database="$TEST_DB" -r 1

    F_Exec /usr/bin/feedex --database="$TEST_DB" --debug --no-learn --parent_category=Hilight --add-entry "test" "test"

fi


if [[ "$1" == 'ling' || "$1" == "all" ]]; then

    TEST_DB="test.db"
    IFILE="test_ifile_ling.json"
    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-entries-from-file "$IFILE"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -r 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" -r 2
    F_Exec /usr/bin/feedex --database="$TEST_DB" -r 3
    F_Exec /usr/bin/feedex --database="$TEST_DB" -r 4
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --keywords 1
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --keywords 2
    

fi



if [[ "$1" == 'actions_fetching' || "$1" == "all" ]]; then

    TEST_DB="test.db"
    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"
    export FEEDEX_DB_PATH="$TEST_DB"

    F_Exec /usr/bin/feedex --debug --add-regex "'[]..\.*aaaa\sd9(][\]][\]]'"

    F_Exec /usr/bin/feedex --debug -L
    F_Exec /usr/bin/feedex --debug -g 1
    F_Exec /usr/bin/feedex --debug -c 2
    F_Exec /usr/bin/feedex --debug -c
    F_Exec /usr/bin/feedex --debug -g
    F_Exec /usr/bin/feedex --debug -u 3
    F_Exec /usr/bin/feedex --debug -u

    F_Exec /usr/bin/feedex --depth=5 --desktop-notify --last -q
    F_Exec /usr/bin/feedex --group=category --depth=5 --desktop-notify --last -q
    F_Exec /usr/bin/feedex --group=flag --depth=5 --desktop-notify --last -q

    F_Exec /usr/bin/feedex --debug -o 1

    F_Exec /usr/bin/feedex --debug --reindex 1
    F_Exec /usr/bin/feedex --debug --relearn 1
    F_Exec /usr/bin/feedex --debug --rerank 2

    F_Exec /usr/bin/feedex --debug --reindex
    F_Exec /usr/bin/feedex --debug --relearn
    F_Exec /usr/bin/feedex --debug --rerank

    F_Exec /usr/bin/feedex --last -q ''

    F_Exec /usr/bin/feedex --keywords 1
    F_Exec /usr/bin/feedex --keywords 2
    F_Exec /usr/bin/feedex --keywords 30
    F_Exec /usr/bin/feedex --keywords 4
    F_Exec /usr/bin/feedex --keywords 5
    F_Exec /usr/bin/feedex --keywords 6


    unset FEEDEX_DB_PATH
fi


if [[ "$1" == 'actions_port' || "$1" == "all" ]]; then

    FEEDS_EXP="exp_feeds_tst.json"
    RULES_EXP="exp_rules_tst.json"
    FLAGS_EXP="exp_flags_tst.json"
    TEST_DB="test.db"
    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"
    [ -f "$FEEDS_EXP" ] && rm "$FEEDS_EXP"
    [ -f "$RULES_EXP" ] && rm "$RULES_EXP"
    [ -f "$FLAGS_EXP" ] && rm "$FLAGS_EXP"

    F_Exec /usr/bin/feedex --debug --export-feeds "$FEEDS_EXP"
    F_Exec /usr/bin/feedex --debug --export-rules "$RULES_EXP"
    F_Exec /usr/bin/feedex --debug --export-flags "$FLAGS_EXP"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --import-feeds "$FEEDS_EXP"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --import-rules "$RULES_EXP"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --import-flags "$FLAGS_EXP"

    F_Exec /usr/bin/feedex --database="$TEST_DB" -L
    F_Exec /usr/bin/feedex --database="$TEST_DB" --list-rules
    F_Exec /usr/bin/feedex --database="$TEST_DB" --list-flags


    F_Exec /usr/bin/feedex --debug --export-feeds "$FEEDS_EXP"
    F_Exec /usr/bin/feedex --debug --export-rules "$RULES_EXP"
    F_Exec /usr/bin/feedex --debug --export-flags "$FLAGS_EXP"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --import-feeds "ssssss$FEEDS_EXP"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --import-rules "ssssss$RULES_EXP"
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --import-flags "ssssss$FLAGS_EXP"

fi

if [[ "$1" == 'actions_add_from_url' || "$1" == "all" ]]; then

    TEST_DB="test.db"
    [ -d "$TEST_DB" ] && rm -r "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-feed 'http://feeds.arstechnica.com/arstechnica/index'
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --add-feed 'https://www.space.com/feeds/all'
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --no-fetch --add-feed 'https://www.theverge.com/rss/index.xml'
    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --handler=local --add-feed 'https://www.siliconvalley.com/feed/'


    F_Exec /usr/bin/feedex --database="$TEST_DB" -L

fi


if [[ "$1" == "gui" ]]; then

    TEST_DB="test.db"
    [ -f "$TEST_DB" ] && rm "$TEST_DB"

    F_Exec /usr/bin/feedex --debug --database="$TEST_DB" --gui

fi