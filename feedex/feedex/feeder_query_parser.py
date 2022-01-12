# -*- coding: utf-8 -*-
""" Query Parser for Feedex"""

from feedex_headers import *







class FeederQueryParser:
    """Class for query parsing and rule matching for Feedex
       Requires an engine (class Feeder instance) to work
       Query types:
            0 - string matching
            1 - Full Text Search
            2 - Full Text Search - no stemming
        additional rule matching types:
            3 - REGEX matching
        types for learned rules:
            4 - Stemmed
            5 - Exact

    """


    def __init__(self, parent, **kargs):

        # Config and parent classes
        self.FX = parent
        self.config = kargs.get('config', DEFAULT_CONFIG)

        # Overload config passed in arguments
        self.debug = kargs.get('debug',False) # Triggers additional info at runtime

        self.ignore_images = kargs.get('ignore_images', self.config.get('ignore_images',False))
        self.wait_indef = kargs.get('wait_indef',False)

        # CLI display options
        self.output = kargs.get('output','cli')
        self.delim = kargs.get('delimiter','|')
        self.delim2 = kargs.get('delimiter2',';')
        self.delim_escape = kargs.get('delim_escape','\\')
        self.trunc = kargs.get('trunc',200)

        self.print = kargs.get('print',False)

        # This tells us if the GUI is running
        self.gui = kargs.get('gui',False)

        # Interface for managing history items
        self.history_item = HistoryItem(self.FX)

        # Container for query results
        self.result = SQLContainer('entries', RESULTS_SQL_TABLE)

        # Query results
        self.results = []

        self.snippets_lst = [] # Snippet lists for query results (string search)

        self.total_result_number = 0 #This is a result number in case a sumary is performed









##############################################################
#
#       QUERY PARSING AND MAIN SEARCH



    def _build_sql(self, phrase:dict, filters:dict, **kargs):
        """ Builds SQL query to get basic lists of results """

        # Construct condition string if search phrase is not empty 
        # Haldle wildcards, beginnings, endings, case sensitivity and such...
        vals = {}
        if not phrase['empty']:

            qtype = filters.get('qtype',0)
            field = filters.get('field')

            vals['phrase'] = phrase['sql']

            # String matching
            if qtype == 0:

                if field is None: cond = "\n(e.title LIKE :phrase  ESCAPE '\\' OR e.desc LIKE :phrase  ESCAPE '\\' OR e.category LIKE :phrase  ESCAPE '\\' OR e.text LIKE :phrase  ESCAPE '\\')\n"
                else: cond = f"\n( {PREFIXES[field]['sql']} LIKE :phrase ESCAPE '\\')\n"

            # Full text search
            elif qtype == 1: cond = "\n( e.tokens LIKE :phrase ESCAPE '\\'  )"
            elif qtype == 2: cond = "\n( e.tokens_raw LIKE :phrase ESCAPE '\\' )"
            elif qtype == 4: cond = "\n( e.tokens LIKE :phrase ESCAPE '\\'  )"
            elif qtype == 5: cond = "\n( e.tokens_raw LIKE :phrase ESCAPE '\\' )"
 

        else: #string is empty
            cond = "\n1=1\n"


        # And this is a core of a query (with column listing from header constant)
        query = f"select {RESULTS_COLUMNS_SQL}\nwhere {cond}"

        #Add filtering according to given parameters
        if filters.get("feed") is not None:
            vals['feed_id'] = scast(filters.get('feed'), int, 0)
            query = f"{query}\nand ( f.id = :feed_id and f.is_category <> 1 )"

        elif filters.get("category") is not None:
            if filters.get("deleted", False): del_str = ''
            else: del_str = 'and coalesce(ff.deleted,0) <> 1'
            vals['feed_id'] = scast(filters.get('category'), int, 0)

            query = f"""{query}\nand (( f.id=:feed_id and f.is_category = 1) 
or f.id in ( select ff.id from feeds ff where ff.parent_id = :feed_id {del_str} ))"""

        if filters.get("id") is not None:
            vals['id'] = scast(filters.get('id'), int, 0)
            query = f"{query}\nand e.id = :id"

        if filters.get("raw_pubdate_from") is not None: 
            query = f"{query}\nand e.pubdate >= :raw_pubdate_from"
            vals['raw_pubdate_from'] = filters['raw_pubdate_from']
        if filters.get("raw_pubdate_to") is not None: 
            query = f"{query}\nand e.pubdate <= :raw_pubdate_to"
            vals['raw_pubdate_to'] = filters['raw_pubdate_to']
        if filters.get("raw_adddate_from") is not None: 
            query = f"{query}\nand e.adddate >= :raw_adddate_from"
            vals['raw_adddate_from'] = filters['raw_adddate_from']
        if filters.get("raw_adddate_to") is not None: 
            query = f"{query}\nand e.adddate <= :raw_adddate_to"
            vals['raw_adddate_to'] = filters['raw_adddate_to']
        

        if filters.get("today", False):
            vals['cdate'] = int(datetime.now().timestamp()) - 86400
            if vals['cdate'] > 0:
                query = f"{query}\nand e.pubdate >= :cdate"

        elif filters.get("last_week", False):
            vals['cdate'] = int(datetime.now().timestamp()) - 604800
            if vals['cdate'] > 0:
                query = f"{query}\nand e.pubdate >= :cdate"

        elif filters.get("last_month", False):
            vals['cdate'] = int(datetime.now().timestamp()) - (86400*31)
            if vals['cdate'] > 0:
                query = f"{query}\nand e.pubdate >= :cdate"

        elif filters.get("last_quarter", False):
            vals['cdate'] = int(datetime.now().timestamp()) - (86400*31*3)
            if vals['cdate'] > 0:
                query = f"{query}\nand e.pubdate >= :cdate"

        elif filters.get("last_six_months", False):
            vals['cdate'] = int(datetime.now().timestamp()) - (86400*31*6)
            if vals['cdate'] > 0:
                query = f"{query}\nand e.pubdate >= :cdate"

        elif filters.get("last_year", False):
            vals['cdate'] = int(datetime.now().timestamp()) - (86400*31*12)
            if vals['cdate'] > 0:
                query = f"{query}\nand e.pubdate >= :cdate"

        elif filters.get('last_hour', False):
            vals['cdate'] = int(datetime.now().timestamp()) - (60*60)
            if vals['cdate'] > 0:
                query = f"{query}\nand e.adddate >= :cdate"

        elif filters.get('last', False):
            vals['cdate'] = self.FX.get_last()
            if vals['cdate'] > 0:
                query = f"{query}\nand e.adddate >= :cdate"


        if filters.get('handler') is not None:
            vals['handler'] = scast(filters.get('handler'), str, '').lower()
            query = f"{query}\nand f.handler = :handler"


        if filters.get("importance",0) != 0:
            vals['importance'] = scast(filters.get('importance'), int, 0)
            query = f"{query}\nand e.importance >= :importance"

        if filters.get("unread",False):
            query = f"{query}\nand coalesce(e.read,0) = 0"
        elif filters.get("read",False):
            query = f"{query}\nand coalesce(e.read,0) > 0"

        if filters.get("flag") is not None:
            if filters.get('flag') == 0:
                query = f"{query}\nand coalesce(e.flag,0) > 0"
            elif filters.get('flag') == -1:
                query = f"{query}\nand coalesce(flag,0) = 0"
            else:  
                vals['flag'] = scast(filters.get('flag',0), int, 0)
                query = f"{query}\nand coalesce(e.flag,0) = :flag"

        if filters.get("deleted",False):
            query = f"{query}\nand (coalesce(e.deleted,0) = 1 or coalesce(f.deleted,0) = 1)"
        elif filters.get("deleted_entries",False):
            query = f"{query}\nand (coalesce(e.deleted,0) = 1)"
        else:
            query = f"{query}\nand coalesce(e.deleted,0) <> 1 and coalesce(f.deleted,0) <> 1"

        # This one is risky, so we have to be very careful every ID is a valis integer
        if filters.get('ID_list') is not None and type(filters.get('ID_list')) in (list,tuple) and len(filters.get('ID_list',[])) > 0:
            ids = ''
            for i in filters.get('ID_list',[]):
                i = scast(i, int, None)
                if i is None: continue
                ids = f'{ids}{i},'
            ids = ids[:-1]
            query = f"{query}\nand e.id in ({ids})"

        # Sorting options
        sort = filters.get('sort')
        rev = filters.get('rev')
        if (sort is not None) and (type(sort) is str) and (len(sort) > 2):
            if sort.startswith('-'):
                desc=True
            else:
                desc=False
            sort = sort[1:]
            if sort not in ENTRIES_SQL_TABLE:
                sys.stderr.write(f"{sort} is not a valid field! Changed to ID")
                sort = 'id'
            query = f"{query}\norder by e.{sort}"
            if desc and not rev:
                query = f"{query} DESC"
            elif not desc and rev:
                query = f"{query} DESC"

        if filters.get('last_n') is not None:
            last_n = scast(filters.get('last_n'), int, None)
            if last_n is not None: 
                query = f"{query}\n"

    

        return query, vals






    def notify(self, **kargs):
        """ Notify about news downloaded during last news check, print them or generate desktop notifications """

        level = kargs.get('notify_level',1)
        rev = kargs.get('rev',False)

        if rev: sql='order by e.importance DESC, e.flag DESC, e.weight DESC'
        else: sql='order by e.importance ASC, e.flag ASC, e.weight ASC'
        last = self.FX.get_last()        
        
        if level == 1:
            self.results = self.FX.curs.execute(NOTIFY_LEVEL_ONE_SQL, {'last':last} ).fetchall()
        elif level == 2:
            self.results = self.FX.curs.execute(NOTIFY_LEVEL_TWO_SQL+sql, {'last':last} ).fetchall()              
        elif level == 3:
            self.results = self.FX.curs.execute(NOTIFY_LEVEL_THREE_SQL+sql, {'last':last} ).fetchall()
        else:
            self.results = self.FX.curs.execute(NOTIFY_LEVEL_TWO_SQL, {'last':last} ).fetchall()
            self.total_result_number = len(self.results)
            if self.total_result_number > level:
                self.results = self.FX.curs.execute(NOTIFY_LEVEL_ONE_SQL, {'last':last} ).fetchall()
                level = 1
            else:
                level = 2

        if kargs.get('print',self.print):

            if level in (2,3):
                self.cli_table_print(RESULTS_SQL_TABLE_PRINT, self.results, flag_col=self.result.get_index('flag'),  
                                    del_col=self.result.get_index('deleted'), read_col=self.result.get_index('read'),
                                    mask=RESULTS_SHORT_PRINT1, number_footnote='new articles', date_col=self.result.get_index('pubdate_short') )
            elif level == 1:
                self.cli_table_print(("Feed (ID)", "All news", "Flagged news"), self.results, flag_col=2, 
                number_footnote='channels have new items', total_number=self.total_result_number, total_number_footnote=' new entries')

        return self.results




######################################################################
#   BASIC QUERY
#

    def query(self, string:str, filters:dict, **kargs):
        """ Main Query method
            Queries database with search string. """
        # This must be done in two stages:
        # SQL query, and phrase matching/filtering on SQL results (to get match count)

        qtype = self.FX.resolve_qtype(filters.get('qtype'))
        if qtype == -1:
            sys.stderr.write('Invalid query type!')
            return -1
        filters['qtype'] = qtype

        
        lang = filters.get('lang', 'heuristic')

        if qtype in (1,2,): self.FX.LP.set_model(lang)

        if filters.get('field') is not None:
            filters['field'] = self.FX.resolve_field(filters.get('field'))
            if filters['field'] == -1:
                sys.stderr.write('Invalid field value!')
                return -1

        if filters.get('category') is not None:
            filters['category'] = self.FX.resolve_category(filters.get('category'))
            if filters['category'] == -1: 
                sys.stderr.write('Category not found!')
                return -1

        if filters.get('feed') is not None:
            filters['feed'] = self.FX.resolve_feed(filters.get('feed'))
            if filters['feed'] == -1:
                sys.stderr.write('Channel ID not found!')
                return -1

        if filters.get('feed_or_cat') is not None:
            filters['feed_or_cat'] = self.FX.resolve_f_o_c(filters.get('feed_or_cat'))
            if filters['feed_or_cat'] == -1:
                sys.stderr.write('Category or Channel not found!')
                return -1
            elif filters['feed_or_cat'][0] == -1:
                filters['category'] = filters['feed_or_cat'][1]
            elif filters['feed_or_cat'][1] == -1:
                filters['feed'] = filters['feed_or_cat'][0]


        if filters.get('last',False): filters['from_added'] = self.FX.get_last()

        rev = filters.get('rev',True)
        sort = filters.get('sort')
        
        case_ins = None
        if filters.get('case_ins') is True:
            case_ins = True
        if filters.get('case_sens') is True: 
            case_ins = False

        if case_ins is None:
            if self._has_caps(string):
                case_ins = False
                filters['case_ins'] = False
            else:
                case_ins = True
                filters['case_ins'] = True
        

        filters['flag'] = self._resolve_flag(filters.get('flag'))

        # Resolve date ranges
        if filters.get('date_from') is not None:
            date = convert_timestamp(filters['date_from'])
            if date is None: return -1
            filters['raw_pubdate_from'] = date
        if filters.get('date_to') is not None:
            date = convert_timestamp(filters['date_to'])
            if date is None: return -1
            filters['raw_pubdate_to'] = date

        if filters.get('date_add_from') is not None:
            date = convert_timestamp(filters['date_add_from'])
            if date is None: return -1
            filters['raw_adddate_from'] = date
        if filters.get('date_add_to') is not None:
            date = convert_timestamp(filters['date_add_to'])
            if date is None: return -1
            filters['raw_add_to'] = date





        rank =  kargs.get('rank',True)
        cnt = kargs.get('cnt',False)

        snippets = kargs.get('snippets',True)
        max_context_length = self.config.get('max_context_length', 500)

        if cnt or rank or snippets: regexify = True
        else: regexify = False

        phrase = self.FX.LP.f_phrase(string, qtype=qtype, case_ins=case_ins, field=filters.get('field'), sqlize=True, regexify=regexify)

        (query, vals) = self._build_sql(phrase, filters)
        if self.debug:
            print(f"\n\nQuery: \n{query}\n{vals}")
            print(f'Phrase: {phrase}')
    
        results_tmp = self.FX.curs.execute(query, vals).fetchall()
        
        if self.debug: print("Results: ", len(results_tmp))

        self.results = []

        # Rank results (if needed)
        # For this we will use last returned column and then replace it with ranking - a little crude, but works
        # SQL has its limitations and I need something beyond boolean matching

        # No point doing this if no string was given or there was only one result
        matched_docs_count = len(results_tmp)
        if (rank or cnt) and (not phrase.get('empty',False)) and matched_docs_count > 0:
            if rank:
                doc_count = kargs.get('doc_count', self.FX.get_doc_count())
                idf = log10(doc_count/matched_docs_count)

            # Calculate ranking for each result
            for r in results_tmp:

                self.result.populate(r)
                if snippets:
                    self.snippets_lst = []
                    snips = []

                (matched, snips) = self.FX.LP.match_fields(phrase, qtype, filters.get('field'), entry=self.result, case_ins=case_ins, snippets=snippets)

                # Append snippets
                if snippets:
                    if qtype in (0, 1, 2,):
                        for s in snips:
                            if len(s) <= max_context_length or max_context_length == 0: # do this to avoid showing long wildcard matches
                                self.snippets_lst.append(s)

                    self.result['snippets'] = self.snippets_lst.copy()

                # Append TF-IDF rank or match count - depending on what option was chosen
                if rank: # Construct TF-IDF
                    doc_len = scast(self.result["word_count"], int, 1)
                    if doc_len == 0: rnk = 0
                    else:
                        tf = matched/doc_len
                        # Final ranking measure - modify at your fancy
                        rnk = tf * idf
                    # append...
                    self.result['rank'] = rnk
                    self.result['count'] = matched

                if cnt:
                    # Append count if it was specified...
                    self.result['count'] = matched

                self.results.append(self.result.tuplify(all=True))

            # Sort results by rank or count if no other sorting method was chosen
            if sort is None:
                if cnt:
                    self.results.sort(key=lambda x: x[self.result.get_index('count')], reverse=-rev)
                elif rank:
                    self.results.sort(key=lambda x: x[self.result.get_index('rank')], reverse=-rev)
        else:
            self.results = results_tmp


        # Save phrase to history        
        if not kargs.get('no_history',False): 
            err = self.history_item.add(phrase, string, filters.get('feed'))
            if err != 0: cli_msg(err)


        # Display results if needed
        if kargs.get('print', self.print):
            columns = kargs.get('columns',RESULTS_SHORT_PRINT1)
            self.cli_table_print(RESULTS_SQL_TABLE_PRINT, self.results, mask=columns, 
                                flag_col=self.result.get_index('flag'), read_col=self.result.get_index('read'), del_col=self.result.get_index('deleted'), 
                                date_col=self.result.get_index('pubdate_short'))
            
        return self.results








####################################################################################################3
#
#       COMPOSITE QUERIES
#




    def find_similar(self, id, **kargs):
        """ Find entry similar to specified by ID based on extracted features """
        id = scast(id, int, 0)
        limit = kargs.get('limit',self.config.get('default_similarity_limit',20)) # Limit results
        rev = kargs.get('rev',False)  # Reverse sort order
        kargs['limit'] = None
        kargs['rev'] = None

        # Get or generate rules
        rules = self.FX.curs.execute("select * from rules where context_id=:id order by weight desc", {'id':id} ).fetchall()
        if rules in (None, [], [None]):    
            entry = EntryContainer(self.FX, id=id)
            if not entry.exists: return -1
            entry.relearn_keywords()

            rules = self.FX.curs.execute("select * from rules where context_id=:id order by weight desc", {'id':id} ).fetchall()
            if rules in (None, [], [None]):
                if self.debug: print("Nothing to find...")
                return 0
        if self.config.get('default_similar_weight', 2) > 0:
            self.FX.run_sql_lock(f"update entries set read = coalesce(read,0) + {self.config.get('default_similar_weight', 2)}  where id = :id", {'id':id} )

        # Search for keywords in entries one by one and record weighted results
        i = 0
        filters = kargs.copy()
        filters['lang'] = kargs.get('lang','heuristic')
        filters['case_ins'] = True
        filters['rev'] = False
        doc_cnt = self.FX.get_doc_count()
        freq_dist = {}

        for r in rules:
            if i >= limit: break

            qphrase = r[self.FX.rule.get_index('string')]

            if r[self.FX.rule.get_index('type')] == 5: filters['qtype'] = 5
            else: filters['qtype'] = 4

            if r[self.FX.rule.get_index('case_insensitive')] == 1: filters['case_ins'] = True
            else: filters['case_ins'] = False
            if r[self.FX.rule.get_index('field_id')] is not None:
                filters['feed'] = r[self.FX.rule.get_index('field_id')]

            self.query(qphrase, filters, rank=False, cnt=True, doc_count=doc_cnt, snippets=False, print=False, no_history=True, )

            if self.results is not None and len(self.results) > 0:
                for rs in self.results:
                    self.result.populate(rs)
                    
                    w = self.result.get('count',0) * coalesce(r[self.FX.rule.get_index('weight')],0) * self.result['weight']
                    freq_dist[self.result['id']] = freq_dist.get(self.result['id'],0) + w
                i += 1

        # Create freq distribution of results-weight
        freq_dist_sorted = []
        for fd, v in freq_dist.items():
            freq_dist_sorted.append((fd, v))
        freq_dist_sorted.sort(key=lambda x: x[-1], reverse=True)
        
        # Construct final list of IDs
        ids=[]
        for i,idd in enumerate(freq_dist_sorted):
            if i >= limit:
                break
            ids.append(idd[0])
        
        # ... and query for them
        if len(ids) > 0:
            results_tmp = self.query('*', {'ID_list': ids} ,rank=False, cnt=False, snippets=False, print=False, no_history=True)
        else:
            results_tmp = []

        self.results = []
        # Append similarity measure at the end of each result to sort by it later
        for r in results_tmp:
            result_tmp = list(r)
            result_tmp.append(None)
            result_tmp.append(None)
            result_tmp[self.result.get_index('rank')] = freq_dist.get(result_tmp[self.result.get_index('id')],0)
            self.results.append(result_tmp)

        self.results.sort(key=lambda x: x[self.result.get_index('rank')], reverse=-rev)

        if kargs.get("print",self.print):
            self.cli_table_print(RESULTS_SQL_TABLE_PRINT, self.results, mask=RESULTS_SHORT_PRINT1, 
                            read_col=self.result.get_index('read'), flag_col=self.result.get_index('flag'), del_col=self.result.get_index('deleted'), 
                            number_footnote='similar documents', date_col=self.result.get_index('pubdate_short'))
    

        else: return self.results







    def term_context(self, string:str, **kargs):
        """ Get term's context (find entries and print immediate surroundings) """
        string = scast(string, str, '')
        if string == '': 
            self.results = ()
            return self.results
        
        self.query(string, kargs, count=False, rank=True, snippets=True, print=False)

        context = SQLContainer('entries', RESULTS_SQL_TABLE_PRINT + ("Context",) )
        
        results_tmp = []
        
        self.total_result_number = len(self.results)

        for r in self.results:    
            self.result.populate(r)

            for s in self.result['snippets']:
                
                fields = self.result.listify(all=True)
                fields.append((s,))
                context.populate(fields)
                results_tmp.append(context.tuplify())

        self.results = results_tmp

        if kargs.get('print',self.print):
            self.cli_table_print(context.fields, self.results, output='cli_noline', 
                                mask=(context.get_index('Date'), context.get_index('Context'), context.get_index('ID'), context.get_index('Source (ID)'), context.get_index('Published - Timestamp'), ), 
                                date_col=context.get_index('Date'), del_col=context.get_index('Deleted?'), read_col=context.get_index('Read'), flag_col=context.get_index('Flag'),
                                total_number=self.total_result_number, total_number_footnote='entries', number_footnote='contexts')
        
        else:
            return self.results




    def term_net(self, term:str, **kargs):
        """ Show terms/features connected to a given term by analising contexts """
        

        term = scast(term, str, '') 
        if term == '': 
            self.results = ()
            return self.results

        self.results = self.FX.curs.execute(TERM_NET_SQL, {'name':term} ).fetchall()
        
        #If the term is not in the rules, query the database
        if self.results in ((),[],None, (None,)):

            filters = {'qtype' : 1, 'lang' : kargs.get('lang','heuristic'), 'case_ins' : True}
            self.query(term, filters, rank=False, cnt=False, snippets=False, print=False)

            if self.results not in ((),[],None, (None,)):
                ids = []
                for r in self.results:
                    id = scast(slist(r, self.result.get_index('id'), 0), int, 0)
                    ids.append( scast(id, str, "''") )
                ids = ', '.join(ids)
            
                # Get rules from entries that input term comes from 
                sql = f"select r.name as name, r.weight as weight, count(r.context_id) as c from rules r where r.context_id in ( {ids} ) group by r.name, r.weight"

                if self.debug: print(sql)

                self.results = self.FX.curs.execute(sql).fetchall()
        
        self.results.sort(key=lambda x: x[1], reverse=kargs.get('rev', False))

        if kargs.get('print',self.print):
            self.cli_table_print(("Term", "Weight", "Documents"), self.results, output='csv')
            if self.debug: print(len(self.results), " results")
        else:
            return self.results






    def terms_for_entry(self, id:int, **kargs):
        """ Output terms/features learned from an entry """
        SQL='select r.name, r.weight from rules r where r.context_id = :id order by r.weight'

        if kargs.get('rev',False): SQL=f'{SQL} DESC'
        else: SQL=f'{SQL} ASC'

        self.results = self.FX.curs.execute(SQL, {'id':id} ).fetchall()
        if self.results in ([],None,[None]) and not kargs.get('no_recalc',False):
            entry = EntryContainer(self.FX, id=id)
            if not entry.exists: return -1
            entry.relearn_keywords()
            self.results = self.FX.curs.execute(SQL, {'id':id} ).fetchall()

        if kargs.get('print',self.print):
            self.cli_table_print(("Term", "Weight"), self.results, output='csv')
            if self.debug: print(len(self.results), " results")
        else:
            return self.results
                



    def rules_for_entry(self, id:int, **kargs):
        """ Output rules that match and contributed to importance of given entry """
        do_print = kargs.get('print',True)
        entry = EntryContainer(self.FX, id=id)
        if not entry.exists: return -1

        rules = entry.matched_rules()
        ostring = f"""Rules matched for entry {entry['id']} ({entry.name()}):
--------------------------------------------------------------------------------------------------------
{rules}
--------------------------------------------------------------------------------------------------------
Importance: {entry['importance']:.3f}, Flag: {entry['flag']:.1f}
Weight: {entry['weight']:.3f}
"""
        if do_print: print(ostring)
        return ostring




    def term_in_time(self, term:str, **kargs):
        """ Get term frequency in time and output as a table of data points or a plot in terminal """
        term = scast(term, str, '')
        if term == '':
            self.results = ()
            return self.results
    
        group = kargs.get('group','daily')
        col_name = 'Month'
        plot = kargs.get('plot',False)
        term_width = kargs.get('term_width',150)

        self.query(term, kargs, rank=False, cnt=True, snippets=False, print=False)

        if len(self.results) == 0:
            self.results = ()
            return ()



        if group == 'hourly':
            col_name = 'Hour'
        elif group == 'daily':
            col_name = 'Day'
        elif group == 'monthly':
            col_name = 'Month'

        freq_dict = {}
        data_points = []
        # Construct data table without zeroes
        for r in self.results:

            self.result.populate(r)
            cnt = scast(self.result['count'], int, 0)
            dtetime = scast(self.result['pubdate'], int, 0)

            if group == 'hourly':
                hour = time.strftime('%Y-%m-%d %H', time.localtime(dtetime)) + ":00:00"
                freq_dict[hour] = freq_dict.get(hour,0) + cnt

            elif group == 'daily':
                day = time.strftime('%Y-%m-%d', time.localtime(dtetime)) + " 00:00:00"
                freq_dict[day] = freq_dict.get(day,0) + cnt
                    
            elif group == 'monthly':
                month = time.strftime('%Y-%m', time.localtime(dtetime)) + "-01 00:00:00"
                freq_dict[month] = freq_dict.get(month,0) + cnt


        max = 0
        for f in freq_dict.keys():
            freq = freq_dict.get(f,0)
            if max < freq:
                max = freq
            data_points.append([f, freq])

        data_points.sort(key=lambda x: x[0], reverse=False)

        date_start = data_points[0][0]
        date_end = data_points[-1][0]

        time_series = []
        ts = date_start

        if group == "hourly":
            time_series.append([date_start[:-3], freq_dict[date_start]])
        elif group == "daily":
            time_series.append([date_start[:-9], freq_dict[date_start]])
        elif group == "monthly":
            time_series.append([date_start[:-12], freq_dict[date_start]])
            
        mon_rel = relativedelta(months=1)
        day_rel = relativedelta(days=1)

        # Populate every step on date, even if there were 0 occurences
        while ts != date_end:
            tst = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            if group == "hourly":
                tst += timedelta(hours=1)
                ts_disp = tst.strftime("%Y-%m-%d %H:%M")
            elif group == "daily":
                tst += day_rel
                ts_disp = tst.strftime("%Y-%m-%d")
            elif group == "monthly":
                tst += mon_rel
                ts_disp = tst.strftime("%Y-%m")
            
            ts = tst.strftime("%Y-%m-%d %H:%M:%S")
            fr = freq_dict.get(ts,0)
            time_series.append([ts_disp,fr])
                    

        if kargs.get('print',self.print) and not plot:
            self.cli_table_print([col_name, "Frequency"], time_series, output='csv')

        if plot:
            self.cli_plot(time_series, max, term_width)

        self.results = time_series
        return time_series





#####################################################################
#
#       MISC DISPLAY METHODS
#
#

    def list_feeds(self, **kargs):
        """Utility for listing feeds (for GUI and CLI)"""
        # This tells us if we want a CLI output
        feeds = self.FX.curs.execute(FEEDS_PRINT_SQL).fetchall()
        if kargs.get("print",self.print):
            self.cli_table_print(FEEDS_SQL_TABLE_PRINT + ("Feedex Category",), feeds, mask=FEEDS_SHORT_PRINT, number_footnote='rergistered channels',
                            del_col=self.FX.feed.get_index('deleted'))
        else: 
            return self.FX.feeds


    def list_categories(self, **kargs):
        """ Lists all categories """
        categories = self.FX.curs.execute(CATEGORIES_PRINT_SQL).fetchall()
        if kargs.get("print",self.print):
                self.cli_table_print(CATEGORIES_PRINT, categories, number_footnote='categories', del_col=3) 
        else: 
            return categories



    def read_feed(self, id:int, **kargs):
        """ Print out detailed feed data """
        lfield = self.FX.curs.execute("select f.*, f1.name from feeds f left join feeds f1 on f1.id = f.parent_id where f.id = :id", {'id':id} ).fetchone()
        return self.cli_feed_print(lfield, to_var=kargs.get('to_var',False))


    def read_entry(self, id:int, **kargs):
        """ Wrapper for displaying an entry """
        lentry = self.FX.curs.execute(f"select {RESULTS_COLUMNS_SQL} where e.id = :id", {'id':id} ).fetchone()
        lrules = self.FX.curs.execute("""select name from rules r where r.context_id = :id""", {'id':id} ).fetchall() 
        if self.debug or kargs.get('to_var',False):
            self.FX.entry.populate(self.FX.curs.execute(f"select * from entries e where e.id = :id", {'id':id} ).fetchone())
            ostring = self.FX.entry.__str__()
            if kargs.get('to_var',False):
                return ostring
            print(ostring)
        else:
            self.cli_entry_print(lentry, lrules)



    def show_rules(self, **kargs):
        """ Show manually added rules """
        self.results = self.FX.curs.execute(PRINT_RULES_SQL).fetchall()
        if kargs.get('print', self.print):
            self.cli_table_print(PRINT_RULES_TABLE, self.results, interline=False, output='csv')
        else:
            return self.results



    def show_history(self, **kargs):
        """ Print search history """
        self.results = self.FX.curs.execute(f'{SEARCH_HISTORY_SQL} asc').fetchall()
        if kargs.get('print', self.print):
            self.cli_table_print(('Search phrase','Date added', 'Date added (raw)',), self.results, 
                                    mask=('Search phrase','Date added'), interline=False, output='csv')
        else:
            return self.results





#######################################################################
#
#           UTILITIES
#




    def _has_caps(self, string):
        """ Checks if a string contains capital letters """
        for c in string:
            if c.isupper(): return True
        return False

    def _resolve_flag(self, flag:str):
        if flag in (None,'','all'): return None

        elif flag == 'all_flags':
            return 0
        elif flag == 'no':
            return -1
        elif flag.isdigit():
            return scast(flag, int, None)
        return None

 




    ##########################################################################3
    #   CLI DISPLAY TOOLS
    #


    def cli_table_print(self, columns:list, table, **kargs):
        """ Clean printing of a given table (list of lists) given delimiter, truncation etc.
            Output can be filtered by mask (displayed column list) """

        output = kargs.get('output', self.output)

        if output == 'json':
            json_string = json.dumps(table)
            print(json_string)
            return json_string

        STERM_NORMAL = self.config.get('TERM_NORMAL', TERM_NORMAL)
        STERM_READ = self.config.get('TERM_READ', TERM_READ)
        STERM_FLAG = self.config.get('TERM_FLAG', TERM_FLAG)
        STERM_DELETED = self.config.get('TERM_DELETED', TERM_DELETED)
        SBOLD_MARKUP_BEG = self.config.get('BOLD_MARKUP_BEG', BOLD_MARKUP_BEG)
        SBOLD_MARKUP_END = self.config.get('BOLD_MARKUP_END', BOLD_MARKUP_END)
        STERM_SNIPPET_HIGHLIGHT = self.config.get('TERM_SNIPPET_HIGHLIGHT', TERM_SNIPPET_HIGHLIGHT)



        number_footnote = kargs.get('number_footnote','results')
    
        total_number = kargs.get('total_number', 0)
        total_number_footnote = kargs.get('total_number_footnote','entries')

        sdelim = f" {self.delim} "
        sdelim2 = f" {self.delim2} "
        delim_escape = self.delim_escape
        if delim_escape not in ('', None): delim_escape = f'{delim_escape}{self.delim}'

        if self.debug: mask = columns
        else: mask = kargs.get('mask',columns)

        # Colored columns
        read_col = kargs.get('read_col', -1)
        flag_col = kargs.get('flag_col', -1)
        del_col  = kargs.get('del_col', -1)

        # Date column - for nice formatting short dates
        date_col = kargs.get('date_col',-1)
        if date_col != -1 and not self.debug:
            today = date.today()
            yesterday = today - timedelta(days=1)
            year = today.strftime("%Y")
            year = f'{year}.'
            today = today.strftime("%Y.%m.%d")
            yesterday = yesterday.strftime("%Y.%m.%d")


        # Print header with columns
        string = ''
        for i in mask:
            if type(i) is int: string = f'{string}{scast(columns[i], str, "").replace(self.delim,delim_escape)}{sdelim}'
            else: string = f'{string}{scast(i, str, "").replace(self.delim,delim_escape)}{sdelim}'
        print(string)

        if output == 'cli': print("\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        # If entries are empty, then inform
        if table == [] or table is None:
            print("<<< EMPTY >>>")
        

        # ... and finally, entry list
        for entry in table:
            string = ''
            # Set text colors
            if output in ('cli', 'cli_noline'):
                cs_beg=STERM_NORMAL
                cs_end=STERM_NORMAL
                if del_col != -1 and scast(slist(entry, del_col, 0), int, 0)  >= 1:
                        cs_end = STERM_NORMAL
                        cs_beg = STERM_DELETED
                elif read_col != -1 and scast(slist(entry, read_col, 0), int, 0)  >= 1:
                        cs_end = STERM_NORMAL
                        cs_beg = STERM_READ
                elif flag_col != -1 and scast(slist(entry, flag_col, 0), int, 0)  >= 1:
                        cs_end = STERM_NORMAL
                        cs_beg = STERM_FLAG

            else:
                cs_beg = ''
                cs_end = ''

            for i in mask:
                sdate = False
                if type(i) is not int:
                    tix = columns.index(i)
                    text = slist(entry, tix, '')
                    if tix == date_col:
                        sdate = True
                else:
                    text = slist(entry,i,'')
                    if date_col != -1 and i == date_col:
                        sdate = True

                if type(text) in (float, int):
                    text = scast( round(text,4), str, '<<NUM?>>')

                elif type(text) in (list, tuple):
                    field_str = ''
                    for s in text:
                        if type(s) is str:
                            field_str = f'{field_str}{sdelim2}{s}'
                        elif type(s) in (list, tuple) and len(s) == 3:
                            if output  in ('cli', 'cli_noline'):
                                field_str = f'{field_str}{sdelim2}{s[0]}{STERM_SNIPPET_HIGHLIGHT}{s[1]}{cs_beg}{s[2]}'
                            else:
                                field_str = f'{field_str}{sdelim2}{s[0]}{SBOLD_MARKUP_BEG}{s[1]}{SBOLD_MARKUP_END}{s[2]}'

                    if field_str.startswith(sdelim2):
                        field_str = field_str.replace(sdelim2,'',1)

                    text = field_str

                elif text is None:
                    if output in ('cli', 'cli_noline'): text = '<NONE>'
                    else: text = ''
                else:
                    text = scast(text, str, '')
                    if output in ('cli', 'cli_noline'):
                        if sdate and not self.debug:
                            text = text.replace(today, 'Today')
                            text = text.replace(yesterday, 'Yesterday')
                            text = text.replace(year,'')

                        text = text.replace(SBOLD_MARKUP_BEG, STERM_SNIPPET_HIGHLIGHT).replace(SBOLD_MARKUP_END, cs_beg)

                field = text
            
                # Truncate if needed
                if self.trunc > 0:
                    field = ellipsize(field, self.trunc)
                    field = field.replace("\n",' ').replace("\r",' ').replace("\t",' ')
                    field = f"{field}{cs_beg}"

                # Delimiter needs to be stripped or escaped (for csv printing etc.)
                string = f"{string}{field.replace(self.delim, delim_escape)}{sdelim}"

        
            print(f"{cs_beg}{string}{cs_end}")
            if output == 'cli': print("\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        if output  in ('cli', 'cli_noline'):
            print(f'{len(table)} {number_footnote}')
            if total_number != 0:
                print(f'{total_number} {total_number_footnote}')






    def cli_plot(self, data_points, max, term_width):
        """ Plots a dataset in a terminal """
        unit = dezeroe(max,1)/term_width

        for dp in data_points:
            x = dp[0]
            y = dp[1]
            length = int(y/unit)
            points = ""
            for l in range(length): points = f"{points}*"
                
            print(x, "|", points, " ", y)








    def cli_entry_print(self, lentry:list, lrules:list):
        """ Displays entry given in a list """
    
        entry = SQLContainer('entries', RESULTS_SQL_TABLE)
        entry.populate(lentry)
        if entry['id'] is None:
            cli_msg((-1,"Entry does not exist!"))
            return -1

        string=f"""
Feed or Category (feed_id): {entry['feed_name_id']}  
----------------------------------------------------------------------------------------------------------
Title:  {entry['title']}
----------------------------------------------------------------------------------------------------------
Descripton (desc):     {entry['desc']}
----------------------------------------------------------------------------------------------------------
Text: {entry['text']}
----------------------------------------------------------------------------------------------------------
Links and enclosures:
{entry['links']}
{entry['enclosures']}
Images:
{entry['images']}
Comments:       {entry['comments']}
----------------------------------------------------------------------------------------------------------
Category:       {entry['category']}
Tags:           {entry['tags']}
Author:         {entry['author']} (contact: {entry['author_contact']})
Publisher:      {entry['publisher']} (contact: {entry['publisher_contact']})
Contributors:   {entry['contributors']}
Published:      {entry['pubdate_r']}    Added:  {entry['adddate_str']}
----------------------------------------------------------------------------------------------------------
ID:             {entry['id']}
Language (lang):       {entry['lang']}
Read? (read):   {entry['read']}
Flagged (flag):        {entry['flag']}
Deleted? (deleted):     {entry['deleted']}
-----------------------------------------------------------------------------------------------------------
Weight:         {entry['weight']}       Importance:     {entry['importance']}
    """
        print(string)
        if lrules is not None and lrules != []:
            print("-------------------------------------------------------------------------------------------------------------------")
            print("Learned Keywords:\n")
            rule_str = ""
            for r in lrules: rule_str += slist(r,0,'') + ";  "
            print(rule_str, "\n\n")











    def cli_feed_print(self, lfeed:list, **kargs):
        """ Prints channel data given in a list """
        MAIN_TABLE=FEEDS_SQL_TABLE_PRINT + ("Category",)
        feed = SQLContainer('feeds', MAIN_TABLE)
        feed.populate(lfeed)

        output = kargs.get('output','cli')
        to_var = kargs.get('to_var',False)

        ostring = ''

        if feed['ID'] is None: print("Feed does not exist!")
        else:
            TABLE=FEEDS_SQL_TABLE + ('parent_id -> name',)
            for i,c in enumerate(feed.tuplify(all=True)):
                if output == 'cli' and not to_var:
                    ostring = f'{ostring}\n---------------------------------------------------------------------------------------------------------------------------------------'
                ostring=f"""{ostring}\n{MAIN_TABLE[i]} ({TABLE[i]}):          {c}"""

            if not to_var: print(ostring)
            return ostring

