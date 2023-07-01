# -*- coding: utf-8 -*-
""" 
Handler class for CLI display and exports

"""

from feedex_headers import *











class FeedexCLI:
    """ CLI Display methods gatherred in one container """


    def __init__(self, **kargs) -> None:
        
        self.config = kargs.get('config', fdx.config)

        # Output flags
        self.output = kargs.get('output','cli')
        if self.output not in ('long','headlines','notes','csv','json','json_dict','html','cli',): self.output = 'cli'
        self.plot = kargs.get('plot',False)

        # CLI display options
        self.delim = kargs.get('delimiter','|')
        self.delim2 = kargs.get('delimiter2',';')
        self.delim_escape = kargs.get('delim_escape','')
        bsl = '\\'
        if self.delim_escape != '': self.delim_escape = f"""{self.delim_escape}{bsl}"""
        self.trunc = kargs.get('trunc',200)
        self.term_width = kargs.get('term_width',150)

        self.read_marker = kargs.get('read_marker','=>  ')
        self.note_marker = kargs.get('note_marker','(*)  ')


        self.snip_beg = kargs.get('bold_beg', self.config.get('BOLD_MARKUP_BEG', BOLD_MARKUP_BEG) )
        self.snip_end = kargs.get('bold_end', self.config.get('BOLD_MARKUP_END', BOLD_MARKUP_END) )

        # Terminal colors
        self.STERM_NORMAL = self.config.get('TERM_NORMAL', TERM_NORMAL)
        self.STERM_READ = self.config.get('TERM_READ', TERM_READ)
        self.STERM_DELETED = self.config.get('TERM_DELETED', TERM_DELETED)
        self.SBOLD_MARKUP_BEG = self.snip_beg
        self.SBOLD_MARKUP_END = self.snip_end
        self.STERM_SNIPPET_HIGHLIGHT = self.config.get('TERM_SNIPPET_HIGHLIGHT', TERM_SNIPPET_HIGHLIGHT)

        # Date strings
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.year = self.today.strftime("%Y")
        self.year = f'{self.year}.'
        self.today = self.today.strftime("%Y.%m.%d")
        self.yesterday = self.yesterday.strftime("%Y.%m.%d")

        # General file output
        self.ofile = kargs.get('ofile')

        # HTML output options
        self.html_template = kargs.get('html_template','')
        self.to_files = kargs.get('to_files',False)
        self.to_files_dir = kargs.get('to_files_dir')
        self.to_files_names = kargs.get('to_files_names','<%id%>.html')        

        # Curtom mask
        self.display_cols = kargs.get('display_cols')

        # Desktop notifier
        self.DN = None


    def connect_DN(self, notifier, **kargs):
        """ Lazily connect desktop notifier """
        if self.DN is None: self.DN = notifier



    def _resolve_display_cols(self, cols:str, container):
        """ Resolve display column list """
        cols = scast(cols, str, '')
        if cols == '': return msg(FX_ERROR_VAL, _('Invalid column list format!'))

        tmp_cols = []
        for c in cols.split(','):
            c = c.lower()
            if c not in container.fields: return msg(FX_ERROR_VAL, _('Invalid display column name: %a'), c)
            tmp_cols.append(c)

        self.display_cols = tmp_cols.copy()
        return 0




    def _line(self, cont, result, **kargs):
    
        mask = coalesce(kargs.get('mask'), cont.fields)
        fields = cont.vals.keys()
        interline = kargs.get('interline',False)
        snip_delim = kargs.get('snip_delim','')
        if snip_delim != '': snip_delim2 = "\n"
        else: snip_delim2 = ''

        line = ''
        line_beg = ''
        line_end = ''
        intline = ''
        vals = []
        cont.populate(result)

        if self.output not in ('csv',):

            if interline: intline = "\n\n\n"
            else: intline = ''

            if coalesce(cont.vals.get('is_node'),0) == 1:
                return f"""{intline}
{TCOLS['WHITE_BOLD']}===================================== {coalesce(cont.vals.get('name'), cont.vals['title'], '<???>')} ({cont.vals['children_no']}) ============================================================================{self.STERM_NORMAL}"""
            

            if coalesce(cont.vals.get('deleted'),0) >= 1 or coalesce(cont.vals.get('is_deleted'),0) >= 1:
                line_beg = f"""{line_beg}{self.STERM_DELETED}"""
                line_end = self.STERM_NORMAL
            else:
                if coalesce(cont.vals.get('flag'),-1) > 0:
                    line_beg = TCOLS.get(fdx.get_flag_color_cli(cont.vals.get('flag',-1)),'')
                    line_end = self.STERM_NORMAL
                elif cont.vals.get('color_cli') is not None:
                    line_beg = TCOLS.get(cont.vals.get('color_cli',-1))            
                    line_end = self.STERM_NORMAL

            if coalesce(cont.vals.get('note'),0) >= 1:
                intline = f'{intline}{self.note_marker}'
            elif coalesce(cont.vals.get('read'),0) >= 1:
                intline = f'{intline}{self.read_marker} '


        cont.humanize()       

        for f in mask:
            
            v = cont.vals[f]
            tp = type(v)
            
            if f in ('snippets','context',) and tp in (list, tuple):
                tstr = ''
                for vv in v:
                    if type(vv) is str: tstr = f"""{tstr}{self.delim2}{vv}"""
                    elif type(vv) in (list, tuple) and len(vv) == 3: 
                        if self.output not in ('csv',): tstr = f'{tstr}{snip_delim}{vv[0]}{self.STERM_SNIPPET_HIGHLIGHT}{vv[1]}{self.STERM_NORMAL}{line_beg}{vv[2]}'
                        else: tstr = f'{tstr}{self.delim2}{vv[0]}{self.SBOLD_MARKUP_BEG}{vv[1]}{self.SBOLD_MARKUP_END}{vv[2]}'
                if self.output not in ('csv',): v = f"""{tstr}{snip_delim2}"""
                else: v = tstr
            elif f in ('pubdate_short',) and tp is str:
                v = humanize_date(v, self.today, self.yesterday, self.year)
            elif f in ('passwd',) and tp is str and v.strip() != '' and not self.output in ('csv',): 
                v = '*********'
            elif v is None:
                v = '<N/A>'
            elif tp is int:
                v = str(v)
            elif tp is float:
                v = str( round(v,4) )
            elif tp is str:
                v = v.replace("\n",' ').replace("\r",' ').replace("\t",' ')                    
                v = v.replace(self.delim, self.delim_escape)
                if self.trunc > 0:
                    v = ellipsize(v, self.trunc)

            line = f"""{line}{self.delim} {v} """
        
        return f"""{intline}{line_beg}{line}{self.delim}{line_end}"""







    def out_table(self, qr, **kargs):
        """ Print results in a table """
        sheader = kargs.get('header')
        sfooter = kargs.get('footer')
        
        results = qr.results
        table = qr.result
        result_no = qr.result_no
        result_no2 = qr.result_no2

        mask = None
        allow_plot = False
        line = False
        footer = ''
        header = ''
        snip_delim = ''
        

        if self.output in ('cli', 'long', 'headlines','notes', 'csv'):

            if isinstance(table, ResultEntry):
                footer = f"""{result_no} {_('results')}"""
                if result_no2 != 0: footer = f"""{footer} {_('out of')} {result_no2} {_('entries')}"""
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols
                elif self.output == 'cli': 
                    line = True
                    mask = RESULTS_SHORT_PRINT
                    snip_delim = "\n\t"
                elif self.output == 'long':
                    line = True
                    mask = RESULTS_SQL_TABLE
                    snip_delim = "\n\t"
                elif self.output == 'headlines': mask = HEADLINES_PRINT
                elif self.output == 'notes':
                    line = True
                    mask = NOTES_PRINT
                elif self.output not in ('csv',): line = True

            elif isinstance(table, ResultContext):
                footer = f"""{result_no} {_('contexts out of ')} {result_no2} {_('entries')}"""
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols
                elif self.output == 'long':
                    mask = CONTEXTS_TABLE
                    line = True
                elif self.output not in ('csv',):
                    mask = CONTEXTS_SHORT_PRINT
                    line = True

            elif isinstance(table, ResultFeed):
                footer = f"""{result_no} {_('items')}"""
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols
                elif self.output == 'long': mask = FEEDS_SQL_TABLE
                elif self.output in ('headlines','notes'): mask = CATEGORIES_PRINT
                elif self.output not in ('csv',): mask = FEEDS_SHORT_PRINT

            elif isinstance(table, ResultFlag):
                footer = f"""{result_no} {_('flags')}"""
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols

            elif isinstance(table, ResultRule):
                footer = f"""{result_no} {_('rules')}"""
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols
                elif self.output in ('long','csv'): mask = RULES_SQL_TABLE_RES
                elif self.output == 'headlines': mask = PRINT_RULES_LEARNED
                else: mask = PRINT_RULES_SHORT

            elif isinstance(table, ResultTerm):
                footer = f"""{result_no} {_('terms')}"""
                if result_no2 != 0: footer = f"""{footer} {_('out of')} {result_no2} {_('entries')}"""
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols
                elif self.output in ('long', 'csv'): mask = TERMS_TABLE
                else: mask = TERMS_TABLE_SHORT

            elif isinstance(table, ResultTimeSeries):
                footer = f"""{result_no} {_('time series points')}"""
                if result_no2 != 0: footer = f"""{footer} {_('out of')} {result_no2} {_('entries')}"""
                allow_plot = True
                if self.display_cols is not None:
                    err = self._resolve_display_cols(self.display_cols, table)
                    if err != 0: return err
                    mask = self.display_cols
                elif self.output in ('long', 'csv'): mask = TS_TABLE
                else: mask = TS_TABLE_SHORT

            elif isinstance(table, ResultHistoryItem):
                footer = f"""{result_no} {_('history items')}"""

            else: footer = f"""{result_no} {_('results')}"""

            header = ''
            for c in coalesce(mask, table.vals.keys()): 
                cname = table.col_names[table.get_index(c)] 
                header = f"""{header}{self.delim} {cname} """
            header = f"""{header}{self.delim}"""

            if self.output not in ('csv',):
                if sfooter is not None: footer = f"""{footer}
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
{sfooter}"""
                if sheader is not None: header = f"""{sheader}
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
{header}"""



        
        if self.plot and allow_plot: 
            print(cli_mu(header))
            self._plot(results, mx=qr.result_max)
            print(cli_mu(footer))
        
        elif self.DN is not None: 
            self.DN.clear()
            self.DN.load(results)
            self.DN.show()

        elif self.output == 'json':

            if self.ofile is not None: save_json(self.ofile, results, check=True)
            else: print_json(results)
            

        elif self.output == 'json_dict':
            
            results_dicts = []
            for r in results:
                table.populate(r)
                results_dicts.append( table.vals.copy() )

            if self.ofile is not None: save_json(self.ofile, results_dicts, check=True)
            else: print_json(results_dicts)



        elif self.output == 'csv':

            if self.ofile is not None:
                if os.path.exists(self.ofile): return msg(FX_ERROR_IO, _("File %a already exists!"), self.ofile)
                csv_str = f"""{header}"""
                for r in results: csv_str = f"{csv_str}\n{self._line(table, r)}"
                try:        
                    with open(self.ofile, 'w') as f: f.write(csv_str)
                    msg(_('Data saved to %a as CSV'), self.ofile)
                except OSError as e: return msg(FX_ERROR_IO, f'{_("Error saving CSV data to %a:")} {e}', self.ofile)
            else:
                print(header)
                for r in results: print(self._line(table, r))
 


        elif self.output == 'html': self.to_html(table.vals.keys(), results)


        else:

            if self.ofile is not None:
                if os.path.exists(self.ofile): return msg(FX_ERROR_IO, _("File %a already exists!"), self.ofile)
                out_str = f"""{clr_mu(header)}"""
                for r in results: out_str = f"{out_str}\n{self._line(table, r, mask=mask, interline=line, snip_delim=snip_delim)}"
                out_str = f"""
                
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
{clr_mu(footer)}"""                
                try:        
                    with open(self.ofile, 'w') as f:
                        f.write(out_str)
                except OSError as e: return msg(FX_ERROR_IO, f'{_("Error saving data to %a:")} {e}', self.ofile)

            else:
                print(cli_mu(header))
                for r in results: print(self._line(table, r, mask=mask, interline=line, snip_delim=snip_delim))
                print(f"""
                      
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
{cli_mu(footer)}""")







    def _plot(self, data_points, **kargs):
        """ Plots a dataset in a terminal """
        mx = kargs.get('mx', 0)
                
        unit = dezeroe(mx,1)/self.term_width

        for dp in data_points:
            x = dp[0]
            y = dp[-1]
            length = int(y/unit)
            points = ""
            for l in range(length): points = f"{points}*"
                
            print(x, "|", points, " ", round(y,3))



###########################################################################
#   Entities
#


    def out_entry(self, entry, **kargs):
        """ Displays entry nicely """
        if not entry.exists: return ''

        do_print = kargs.get('do_print',True)
        if fdx.debug_level not in (0, None): 
            if do_print: print(entry)
            return entry.__str__()

        summarize = kargs.get('summarize')
        if summarize is not None: entry.summarize(summarize, separator="(...)\n")

        disp_str = f"""
{_('Feed or Category')} (feed_id): <b>{entry.vals['feed_id']} ({fdx.get_feed_name(entry['feed_id'], with_id=False)})</b>  
----------------------------------------------------------------------------------------------------------
{_('Title:')}  <b>{entry.vals['title']}</b>
----------------------------------------------------------------------------------------------------------
{_('Descripton')} (desc):     <b>{entry.vals['desc']}</b>
----------------------------------------------------------------------------------------------------------
{_('Text')} (text): <b>{scast(entry.vals['text'], str, '')}</b>
----------------------------------------------------------------------------------------------------------
{_('Links and enclosures:')}
<b>{entry.vals['links']}
{entry.vals['enclosures']}</b>
{_('Images')}:
<b>{entry.vals['images']}</b>
{_('Comments')}:       <b>{entry.vals['comments']}</b>
----------------------------------------------------------------------------------------------------------
{_('Category')}:       <b>{entry.vals['category']}</b>
{_('Tags')}:           <b>{entry.vals['tags']}</b>
{_('Author')}:         <b>{entry.vals['author']}</b> ({_('contact')}: <b>{entry.vals['author_contact']}</b>)
{_('Publisher')}:      <b>{entry.vals['publisher']}</b> ({_('contact')}: <b>{entry.vals['publisher_contact']}</b>)
{_('Contributors')}:   <b>{entry.vals['contributors']}</b>
{_('Published')}:      <b>{entry.vals['pubdate_str']}</b>    {_('Added')}:  <b>{entry.vals['adddate_str']}</b>
----------------------------------------------------------------------------------------------------------
{_('ID')}:             <b>{entry.vals['id']}</b>
{_('Language')} (lang):       <b>{entry.vals['lang']}</b>
{_('Read?')} (read):   <b>{entry.vals['read']}</b>
{_('Flagged')} (flag):        <b>{entry.vals['flag']}</b>
{_('Deleted?')} (deleted):     <b>{entry.vals['deleted']}</b>
-----------------------------------------------------------------------------------------------------------
{_('Weight')}:         <b>{entry.vals['weight']}</b>       {_('Importance')}:     <b>{entry.vals['importance']}</b>
"""
        entry.ling(index=False, rank=False, learn=True, save_rules=False)
        kwd_str = ''
        for k in entry.rules: kwd_str = f"""{kwd_str}{k['name']} ({round(k['weight'],3)}); """

        if kwd_str != '': disp_str = f"""{disp_str}
------------------------------------------------------------------------------------------------------------
{_('Keywords')}: <b>{kwd_str}</b>
"""
        if do_print: print(cli_mu(disp_str))
        return clr_mu(disp_str)








    def out_entry_ranking(self, entry, **kargs):
        """ Output keywords for a given entry """
        if not entry.exists: return ''
        
        importance, flag, best_entries, flag_dist, results = entry.ling(index=False, rank=True, to_disp=True)

        qr = FeedexQueryInterface()
        qr.result = ResultRule()
        qr.results = results
        qr.result_no = len(results)
        qr.result_no2 = 0

        header = f"""{_('Rules matched for entry')} <b>{entry.vals['id']} ({entry.name()})</b>:"""
        footer = f"""
{_('Calculated Importance:')} <b>{importance:.3f}</b>, {_('Calculated Flag:')} <b>{flag:.0f}</b>
{_('Saved Importance:')} <b>{entry.vals['importance']:.3f}</b>, {_('Saved Flag:')} <b>{entry.vals['flag']:.0f}</b>
{_('Weight:')} <b>{entry.vals['weight']:.3f}</b>
--------------------------------------------------------------------------------------------------------
{_('Flag distriution:')}<b>"""

        for f,v in flag_dist.items(): footer = f"""{footer} {fdx.get_flag_name(f)} ({f}): {v:.3f}"""

        footer = f"""{footer}</b>
--------------------------------------------------------------------------------------------------------
{_('Most similar read Entries:')}<b>"""

        for e in best_entries: footer = f"""{footer} {e}; """

        footer = f"""{footer}</b>
"""
        self.display_cols = ','.join(PRINT_RULES_FOR_ENTRY)
        self.out_table(qr, header=header, footer=footer)







    def out_feed(self, feed, **kargs):
        """ Nice print feed"""
        if not feed.exists: return ''

        do_print = kargs.get('do_print', True)

        if fdx.debug_level not in (0, None):
            if do_print: print(feed)
            return feed.__str__()

        disp_vals = feed.vals.copy()
        feed.get_parent()
        disp_vals['parent_name'] = fdx.get_feed_name(feed['parent_id'])
        if scast(disp_vals['passwd'], str, '').strip() != '': disp_vals['passwd'] = '*********'

        DISP_LIST = FEEDS_SQL_TABLE_PRINT + (_('Parent Category Name'),)

        disp_str = ''
        for i,d in enumerate(disp_vals.items()):
            k,v = d[0], d[1]
            disp_str = f"""{disp_str}
{DISP_LIST[i]} ({k}): <b>{v}</b>"""

        if do_print: print(cli_mu(disp_str))
        return clr_mu(disp_str)








    def out_test_regex(self, feed, **kargs):
        """ Nice print REGEX testing for feed """
        if not feed.exists: return ''
        handler = FeedexHTMLHandler(feed.DB)        
        handler.set_feed(feed)

        feed_title, feed_pubdate, feed_img, feed_charset, feed_lang, entry_sample, entries = handler.test_download(force=True)

        demo_string = f"""{_('Feed title:')} <b>{feed_title}</b>
{_('Feed Published Date:')} <b>{feed_pubdate}</b>
{_('Feed Image Link:')} <b>{feed_img}</b>
{_('Feed Character Encoding:')} <b>{feed_charset}</b>
{_('Feed Language Code:')} <b>{feed_lang}</b>
------------------------------------------------------------------------------------------------------------------------------

"""
        for e in entries:

            demo_string = f"""{demo_string}
    ------------------------------------------------------------------
    {_('Title:')} <b>{e.get('title')}</b>
    {_('Link:')} <b>{e.get('link')}</b>
    {_('GUID:')} <b>{e.get('guid')}</b>
    {_('Published:')} <b>{e.get('pubdate')}</b>
    {_('Description:')} <b>{e.get('desc')}</b>
    {_('Category:')} <b>{e.get('category')}</b>
    {_('Author:')} <b>{e.get('author')}</b>
    {_('Additional Text:')} <b>{e.get('text')}</b>
    {_('Image HREFs:')} <b>{e.get('images')}</b>"""

        demo_string = f"""{demo_string}
------------------------------------------------------------------------------------------------------------------------------
<i>{_('Entry sample:')}</i>
{entry_sample}
"""
        print(cli_mu(demo_string))









    def out_db_stats(self, stats, **kargs):
        """ Nice print db stats """
        stat_str=f"""

{_('Statistics for database')}: <b>{stats['db_path']}</b>

{_('FEEDEX version')}:          <b>{stats['version']}</b>

{_('Main database size')}:      <b>{stats['db_size']}</b>
{_('Index size')}:              <b>{stats['ix_size']}</b>
{_('Cache size')}:              <b>{stats['cache_size']}</b>

{_('Total size')}:              <b>{stats['total_size']}</b>



{_('Entry count')}:             <b>{stats['doc_count']}</b>
{_('Last entry ID')}:           <b>{stats['last_doc_id']}</b>

{_('Learned rule count')}:      <b>{stats['rule_count']}</b>
{_('Manual rule count')}:       <b>{stats['user_rule_count']}</b>

{_('Feed count')}:              <b>{stats['feed_count']}</b>
{_('Category count')}:          <b>{stats['cat_count']}</b>

{_('Last news update')}:        <b>{stats['last_update']}</b>
{_('First news update')}:       <b>{stats['first_update']}</b>

"""
        if stats['lock']: 
            stat_str = f"""{stat_str}
{_('DATABASE LOCKED')}


"""
        if stats['fetch_lock']: 
            stat_str = f"""{stat_str}
{_('DATABASE LOCKED FOR FETCHING')}


"""

        if stats['due_maintenance']: 
            stat_str = f"""{stat_str}
{_('DATABASE MAINTENANCE ADVISED')}
{_('Use')} <b>feedex --db-maintenance</b> {_('command')}


"""
        print(cli_mu(stat_str))









###############################################################################
#   Exporting to HTML
#

    def htmlize(self, text):
        """ Convert text to html """
        if type(text) in (tuple, list):
            snips = ''
            for s in text:
                if type(s) not in (list,tuple): return ''
                if len(s) != 3: return ''
                snips = f"""{snips}{self.delim2}{self.htmlize(s[0])}{self.snip_beg}{self.htmlize(s[1])}{self.snip_end}{self.htmlize(s[2])}"""
            text = snips
        else:
            text = scast(text, str, '')
        for ent in HTML_ENTITIES_REV: 
            if ent[0] != '': text = text.replace(ent[0],ent[1])
        return text

    def fname(self, text):
        """ Sanitize file name fields """
        if type(text) in (list, tuple): return ''
        text = scast(text, str, '')
        text = text[:50]
        text = text.replace('/','_').replace('"','_').replace("'",'_').replace("""\'""",'_').replace("\n",'_').replace("\r","_").replace(' ','_')
        return text


    def to_html(self, fields:list, table:list, **kargs):
        """ Converts table into a html string from a template """
        #Read template file
        try:
            with open(self.html_template, 'r') as f: templ = f.read()
        except OSError: return msg(FX_ERROR_IO, _("Error reading template file %a!"), self.html_template)

        if self.to_files:
            if not os.path.isdir(self.to_files_dir): return msg(FX_ERROR_IO, _("Target directory %a does not exist! Aborting..."), self.to_files_dir)


        for row in table:
            text = templ
            for i,f in enumerate(fields):
                text = text.replace(f'<%{f}%>', self.htmlize( slist(row,i,'') ) )
            
            if self.to_files:
                file_name = self.to_files_names
                for i,f in enumerate(fields):
                    file_name = file_name.replace(f'<%{f}%>', self.fname( slist(row,i,'') ) )

                target_file = f'{self.to_files_dir}/{file_name}'
                if os.path.isfile(target_file) or os.path.isfile(target_file):
                    return msg(FX_ERROR_IO, _("File %a already exists!"), target_file)

                try:
                    with open(target_file, 'w') as ff: ff.write(text)
                except OSError as e: return msg(FX_ERROR_IO, f'{_("Error writing to file ")}{target_file}: %a', e)

            else: print(text)

        return 0
