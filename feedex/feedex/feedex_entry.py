# -*- coding: utf-8 -*-
""" Entities classes: entries

"""


from feedex_headers import *



class FeedexEntry(SQLContainerEditable):
    """ Container for Entries """

    def __init__(self, db, **kargs):

        SQLContainerEditable.__init__(self, 'entries', ENTRIES_SQL_TABLE, types=ENTRIES_SQL_TYPES, col_names=ENTRIES_SQL_TABLE_PRINT, **kargs)
        self.set_interface(db)
        self.DB.cache_feeds()
        self.DB.cache_flags()

        self.reindex = False # These flags mark the need to reindex and relearn keywords
        self.relearn = False

        self.feed = ResultFeed()
        self.term = FeedexKwTerm()

        self.immutable = ENTRIES_TECH_LIST

        if kargs.get('id') is not None: self.get_by_id(kargs.get('id'))
        elif kargs.get('url') is not None: self.get_by_url(kargs.get('url'))

        # Strings to index in Xapian
        self.ix_strings = {}
        # Strings used for full text ranking
        self.rank_string = ''
        # String to extract features from
        self.learning_string = ''

        # Source link (useful as a feature and independent of db structure)
        self.source_url = None

        self.terms = [] # Keywords extracted by LP








    def get_by_id(self, id:int):
        id = scast(id, int, -1) 
        content = self.DB.qr_sql("select * from entries e where e.id = :id", {'id':id}, one=True )
        if content in (None, (None,), ()):
            self.exists = False
            return msg(FX_ERROR_NOT_FOUND, f"""{_('Entry')} %a {_('not found!')}""", id)
        else:
            self.exists = True
            self.populate(content)
            return 0

    def get_by_url(self, url:str):
        url = scast(url, str, -1)
        content = self.DB.qr_sql("select * from entries e where e.link = :url", {'url':url}, one=True )
        if content in (None, (None,), ()):
            self.exists = False
            return msg(FX_ERROR_NOT_FOUND, f"""{_('Entry with url')} %a {_('not found!')}""", url)
        else:
            self.exists = True
            self.populate(content)
            return 0

    def get_by_ix_id(self, id:int):
        id = scast(id, int, -1)
        content = self.DB.qr_sql("select * from entries e where e.ix_id = :id", {'id':id}, one=True )
        if content in (None, (None,), ()):
            self.exists = False
            return msg(FX_ERROR_NOT_FOUND, f"""{_('Entry')} indexed as %a {_('not found!')}""", id)
        else:
            self.exists = True
            self.populate(content)
            return 0




    def set_feed(self, **kargs):
        """ Setup feed for processing """
        if kargs.get('feed') is not None:
            feed = kargs.get('feed')
            if feed[self.feed.get_index('id')] != self.feed['id']: self.feed.populate(feed)
        else:
            if self.feed['id'] != self.vals['feed_id']:
                feed = fdx.find_f_o_c(self.vals['feed_id'], load=True)
                if feed != -1: self.feed.populate(feed)





    def open(self, **kargs):
        """ Open in browser """
        if not self.exists: return FX_ERROR_NOT_FOUND

        read = coalesce(self.vals['read'],0)


        if self.vals.get('link') is not None:

            now = datetime.now()
            now_raw = int(now.timestamp())
            now = now.strftime('%Y-%m-%d %H:%M:%S')

            if read >= 0: err = self.DB.run_sql_lock('update entries set read = coalesce(read,0) + 1, adddate = :now_raw, adddate_str = :now where id = :id', 
                                                    {'id':self.vals['id'], 'now':now, 'now_raw':now_raw})
            else: err = self.DB.run_sql_lock('update entries set read = 1, adddate = :now_raw, adddate_str = :now  where id = :id', 
                                            {'id':self.vals['id'], 'now':now, 'now_raw':now_raw})
            if err != 0: return FX_ERROR_DB

            self.vals['read'] = read + 1
            self.vals['adddate'] = now_raw
            self.vals['adddate_str'] = now

            err = fdx.ext_open('browser', self.vals.get('link'), background=kargs.get('background',True))
            if err != 0: return err
            else: msg(_('Opening in browser (%a) ...'), self.vals.get('link', '<UNKNOWN>'))


        else: return msg(FX_ERROR_NOT_FOUND, _('No link found. Aborting...'))



        if self.config.get('use_keyword_learning', True) and read == 0: learn = True
        else: learn = False

        # Reindex and learn
        if learn: msg(_('Reindexing and learning keywords...'))
        else: msg(_('Reindexing ...'))
        
        err = self.ling(learn=learn, index=True, rank=False, save_terms=learn)
        if err != 0:
            self.DB.close_ixer(rollback=True)
            return err
        else:
            self.DB.close_ixer()
            msg(_('Keywords learned'))
            err = self.DB.update_stats( {self.vals['feed_id']:1} )

        return err                        







    def validate(self, **kargs):
        """ Field validation """
        if self.vals['flag'] not in (0,None): self.vals['flag'] = fdx.find_flag(self.vals['flag'])
        if self.vals['flag'] == -1: return FX_ERROR_VAL, _('Flag not found!')

        err_fld = self.validate_types()
        if err_fld != 0: return FX_ERROR_VAL, _('Invalid type for field %a'), err_fld

        if self.vals.get('feed_or_cat') is not None:
            feed = fdx.find_f_o_c(self.vals.get('feed_or_cat'), load=True)
            if feed == -1: return FX_ERROR_VAL, _('Channel or Category %a not found!'), self.vals.get('feed_or_cat', '<???>')
            self.feed.populate(feed)
            self.vals['feed_id'] = self.feed['id']

        elif self.vals.get('feed_id') is not None:
            feed = fdx.find_f_o_c(self.vals.get('feed_id'), load=True)
            if feed == -1: return FX_ERROR_VAL, _('Channel or Category %a not found!'), self.vals.get('feed_id', '<???>')
            self.feed.populate(feed)
            self.vals['feed_id'] = self.feed['id']

        elif self.vals.get('parent_id') is not None:
            feed = fdx.find_f_o_c(self.vals.get('parent_id'), load=True)
            if feed == -1: return FX_ERROR_VAL, _('Channel or Category %a not found!'), self.vals.get('parent_id', '<???>')
            self.feed.populate(feed)
            self.vals['feed_id'] = self.feed['id']

        elif self.vals.get('parent_category') is not None:
            feed = fdx.find_category(self.vals.get('parent_category'), load=True)
            if feed == -1: return FX_ERROR_VAL, _('Category %a not found!'), self.vals.get('parent_category', '<???>')
            self.feed.populate(feed)
            self.vals['feed_id'] = self.feed['id']

        else:
            if self.vals.get('feed') is not None: self.vals['feed_id'] = self.vals.get('feed')
            feed = fdx.find_feed(self.vals.get('feed_id'), load=True)
            if feed is None: return FX_ERROR_VAL, _('Every entry needs to be assigned to a Channel or a Category!')
            if feed == -1: return FX_ERROR_VAL, _('Channel %a not found!'), self.vals['feed_id']
            self.feed.populate(feed)
            self.vals['feed_id'] = self.feed['id']


        if self.vals.get('link') is not None and not check_url(self.vals.get('link')):
            return FX_ERROR_VAL, _('Not a valid url! (%a)'), self.vals.get('link', '<???>')

        if self.vals['deleted'] not in (None, 0, 1): return FX_ERROR_VAL, _('Deleted flag must be 0 or 1!')
        
        if self.vals['note'] not in (None, 0,1): return FX_ERROR_VAL, _('Note marker must be 0 or 1!')

        if coalesce(self.vals['read'],0) < 0: return FX_ERROR_VAL, _('Read marker must be >= 0!')

        date = convert_timestamp(self.vals['pubdate_str'])
        if date is None: return FX_ERROR_VAL, _('Invalid published date string (pubdate_str)!')
        else: self.vals['pubdate'] = date

        if self.vals['adddate_str'] is not None:
            date = convert_timestamp(self.vals['adddate_str'])
            if date is None: return FX_ERROR_VAL, _('Invalid adding date string (%a)!'), self.vals['adddate_str']
            else: self.vals['adddate'] = date

        return 0






    def do_update(self, **kargs):
        """ Apply edit changes to DB """
        if not self.updating: return 0
        if not self.exists: return FX_ERROR_NOT_FOUND

        stats_delta = {}

        self.vals['adddate_str'] = datetime.now()

        if kargs.get('validate', True): 
            err = self.validate()
            if err != 0: 
                self.restore()
                return msg(*err)

        if coalesce(self.vals['deleted'],0) == 0 and coalesce(self.backup_vals['deleted'],0) >= 1: 
            stats_delta['dc'] = 1
            restoring = True
        else: 
            restoring = False

        self.relearn = False
        self.reindex = False
        if restoring: self.reindex = True

        err = self.constr_update()
        if err != 0:
            self.restore()
            return err


        for f in self.to_update:
            if f in REINDEX_LIST: self.reindex = True
            
        read = coalesce(self.vals['read'],0)
        old_read = coalesce(self.backup_vals['read'],0)

        if self.config.get('use_keyword_learning', True):
            if self.reindex and read > 0: self.relearn = True
            if read > 0 and old_read <= 0: self.relearn = True

        if restoring and read > 0: stats_delta[self.vals['feed_id']] = read
        elif read != old_read: stats_delta[self.vals['feed_id']] = read - old_read

        if self.relearn or self.reindex:
            if self.reindex:  msg(_('Reindexing statistics ...'))
            if self.relearn: msg(_('Extracting and learning keywords ...'))

            err = self.ling(index=self.reindex, rank=False, learn=self.relearn, save_terms=self.relearn)
            if err != 0:
                self.restore()
                self.DB.close_ixer(rollback=True)
                return err


        # Construct second time, to include recalculated fields
        err = self.constr_update()
        if err != 0:
            self.restore()
            self.DB.close_ixer(rollback=True)
            return err

        err = self.DB.run_sql_lock(self.to_update_sql, self.filter(self.to_update))
        if err != 0:
            self.restore()
            self.DB.close_ixer(rollback=True)
            return err
        else:
            err = self.DB.close_ixer()
            if err != 0:
                self.restore()
                err = self.DB.run_sql_lock(self.to_update_sql, self.filter(self.to_update))
                if err != 0: return msg(FX_ERROR_DB, _('Error restoring entry! Update failed miserably'))
                else: return FX_ERROR_INDEX


        if self.DB.rowcount > 0:

            for i,u in enumerate(self.to_update):
                if u in self.immutable or u == 'id': del self.to_update[i]

            if stats_delta != {}:
                err = self.DB.update_stats(stats_delta)
                if err != 0: return err

            if len(self.to_update) > 1: msg(_('Entry %a updated successfuly!'), self.vals['id'], log=True)
            else:
                for f in self.to_update:
                    if f == 'read' and self.vals.get(f,0) > 0: 
                        msg(_('Entry %a marked as read'), self.vals['id'], log=True)
                    elif f == 'read' and self.vals.get(f,0) < 0: 
                        msg(_('Entry %a marked as read'), self.vals['id'], log=True)
                    elif f == 'read' and self.vals.get(f) in (0, None): 
                        msg(_('Entry %a marked as unread'), self.vals['id'], log=True)
                    elif f == 'flag' and self.vals.get(f) in (0,None): 
                        msg(_('Entry %a unflagged'), self.vals['id'], log=True)
                    elif f == 'flag' and self.vals.get(f) not in (0, None): 
                        msg(_('Entry %a flagged'), self.vals['id'], log=True)
                    elif f == 'deleted' and self.vals.get(f) in (0, None): 
                        msg(_('Entry %a restored'), self.vals['id'], log=True)
                    elif f == 'note' and self.vals.get(f) in (0, None): 
                        msg(_('Entry %a marked as news item'), self.vals['id'], log=True)
                    elif f == 'note' and self.vals.get(f) == 1: 
                        msg(_("""Entry %a marked as a user's Note"""), self.vals['id'], log=True)
                    elif f == 'feed_id': 
                        msg(_("Entry %a assigned to %b"), self.vals['id'], self.feed.name(with_id=True), log=True)
                    elif f == 'node_id' and self.vals.get(f) in (0, None): 
                        msg(_('Entry %a unassigned from node'), log=True)
                    elif f == 'node_id' and self.vals.get(f) not in (0, None): 
                        msg(_('Entry %a assigned to entry %b'),self.vals["id"], self.vals['node_id'], log=True)
                    else:
                        msg(_("Entry %a updated: %b -> %c"), self.vals['id'], f, self.vals.get(f,_("<NULL>")), log=True)
            return 0

        else: return msg(_('Nothing done'))





    def update(self, idict, **kargs):
        """ Quick update with a value dictionary"""
        if not self.exists: return FX_ERROR_NOT_FOUND
        err = self.add_to_update(idict)
        if err == 0: err = self.do_update(validate=True)
        return err




    def delete(self, **kargs):
        """ Delete from DB with terms if necessary """   
        if not self.exists: return FX_ERROR_NOT_FOUND
        id = kargs.get('id', None)
        if id is not None and self.vals['id'] is None: self.get_by_id(id)
        id = self.vals.get('id')
        if id is None: return FX_ERROR_NOT_FOUND

        stats_delta = {}

        if self.vals.get('deleted',0) == 1:
            err = self.DB.run_sql_multi_lock(
                ("delete from terms where context_id = :id", {'id':id}),\
                ("delete from entries where id = :id", {'id':id}) )
        else:
            now = datetime.now()
            now_raw = convert_timestamp(now)
            self.vals['deleted'] = 1
            err = self.DB.run_sql_lock("update entries set deleted = 1, adddate = :now_raw, adddate_str = :now where id = :id", {'id':id, 'now':now, 'now_raw':now_raw} )
            if err == 0:
                # Remove from index ...
                self.DB.connect_ixer()
                try: ix_doc = self.DB.ixer_db.get_document(self.vals['ix_id'])
                except (xapian.DocNotFoundError,): ix_doc = None
                if isinstance(ix_doc, xapian.Document):
                    uuid = ix_doc.get_data()
                    try: self.DB.ixer_db.delete_document(f"""UUID {uuid}""")
                    except xapian.DatabaseError as e: 
                        msg(FX_ERROR_INDEX, _('Index error: %a'), e)
                        self.DB.close_ixer(rollback=True)
                        err = self.DB.run_sql_lock("update entries set deleted = 0 where id = :id", {'id':id})
                        if err != 0: return msg(FX_ERROR_DB, _('Error reverting changes! Delete failed miserably'))
                
                err = self.DB.close_ixer()
                if err != 0:
                    err = self.DB.run_sql_lock("update entries set deleted = 0 where id = :id", {'id':id})
                    if err != 0: return msg(FX_ERROR_DB, _('Error reverting changes! Delete failed miserably'))
            
            stats_delta['dc'] = -1
            stats_delta[self.vals['feed_id']] = -coalesce(self.vals['read'],0)

        if err != 0: return err



        if self.DB.rowcount > 0:

            im_file = os.path.join(self.DB.img_path, f"""{id}.img""")
            if os.path.isfile(im_file):
                try: os.remove(im_file)
                except (OSError, IOError,) as e: msg(FX_ERROR_IO, f"""{_('Error removing image %a')}: {e}""", im_file)

            err = self.DB.update_stats(stats_delta)
            if err != 0: return err

            if self.vals.get('deleted',0) == 1:
                self.vals['deleted'] = 2
                self.exists = False 
                return msg(_('Entry %a deleted permanently with learned terms'), id, log=True)
            else:
                self.vals['deleted'] = 1
                return msg(_('Entry %a deleted'), id, log=True)
        else:                
            return msg(_('Nothing done'))







    def add(self, **kargs):
        """ Add this entry to database """
        counter = kargs.get('counter',0)

        idict = kargs.get('new')
        if idict is not None:
            self.clear()
            self.merge(idict)

        now = datetime.now()
        
        self.vals['id'] = None
        self.vals['adddate_str'] = now
        self.vals['pubdate_str'] = coalesce(self.vals.get('pubdate_str', None), now)
        self.vals['read'] = coalesce(self.vals.get('read'), self.config.get('default_entry_weight',2))
        self.vals['note'] = coalesce(self.vals['note'],1)

        if kargs.get('validate',True):
            err = self.validate()
            if err != 0: return msg(*err)

        if not self.config.get('use_keyword_learning', True): learn = False
        elif coalesce(self.vals['read'], 0) > 0: learn = True
        else: learn = False

        if kargs.get('ling',True):
            err = self.ling(index=True, rank=True, learn=learn, save_terms=False, counter=counter)
            if err != 0:
                self.DB.close_ixer(rollback=True)
                return err

        else: learn = False

        self.clean()
        err = self.DB.run_sql_lock(self.insert_sql(all=True), self.vals)
        if err != 0: 
            self.DB.close_ixer(rollback=True)
            return err

        self.vals['id'] = self.DB.lastrowid
        self.DB.last_entry_id = self.vals['id']
    
        err = self.DB.close_ixer()
        if err != 0:
            err = self.DB.run_sql_lock('delete from entries where id = :id', {'id':self.vals['id']})
            if err != 0: return msg(FX_ERROR_DB, _('Could not revert changes! Add failed miserably'))
            else: return FX_ERROR_INDEX

        if learn:
            msg(_('Extracting and learning keywords ...'))
            err = self.save_terms()
            if err != 0: return msg(FX_ERROR_DB,_('Error saving learned keywords!'))
            else: msg(_('Keywords learned for entry %a'), self.vals['id'])

        if kargs.get('update_stats',True):
            stats_delta = { 'dc':1, self.vals['feed_id']:coalesce(self.vals['read'],0) }
            err = self.DB.update_stats(stats_delta)
            if err != 0: return err

            if not fdx.single_run: 
                err = self.DB.load_terms()
                if err != 0: return msg(FX_ERROR_DB, _('Error reloading learned terms after successfull add!'))


        if self.vals['note'] in (0,None): return msg(_('Entry %a added as News item'), self.vals['id'])
        else: return msg(_('Entry %a added as a Note'), self.vals['id'])











    ###############################################
    #  Linguistic processing methods

    def ling(self, **kargs):
        """ Linguistic processing coordinator """

        learn = kargs.get('learn',False)
        stats = kargs.get('stats',True)
        rank = kargs.get('rank',True)
        save_terms = kargs.get('save_terms', learn)
        index = kargs.get('index', stats)
        to_disp = kargs.get('to_disp',False)
        counter = kargs.get('counter',0) # Counter for generating UUIDs
        rebuilding = kargs.get('rebuilding',False) # This tells if we are creating index anew and, if yes, we clear IX_IDs

        # LP lazy load and caching
        self.DB.connect_LP()
        if rank: self.DB.cache_rules()
        if learn: self.DB.cache_terms()

        # Setup language and remember if detection was tried
        self.vals['lang'] = self.DB.LP.set_model(self.vals['lang'], sample=f"""{self.vals['title']} {self.vals['desc']}"""[:1000])

        self.set_feed()


        if index or rank: 
            self.ix_strings, self.rank_string = self.DB.LP.index(self.vals)
            if stats: 
                self.DB.LP.calculate_stats()
                self.merge(self.DB.LP.stats)            
        

        
        
        if rank:
            # Perform ranking based on rules. Construct ranking string for stemmed rules
            if not to_disp:
                self.vals['importance'], self.vals['flag'] = self.DB.LP.rank(self.vals, self.rank_string, to_disp=False)
            else:
                return self.DB.LP.rank(self.vals, self.rank_string, to_disp=True)     
            


            
        if index:
            self.DB.connect_ixer()

            # Remove doc if exists ...
            if rebuilding or self.vals['ix_id'] is None: ix_doc = None
            else:
                try: ix_doc = self.DB.ixer_db.get_document(self.vals['ix_id'])
                except (xapian.DocNotFoundError,): ix_doc = None
                except (xapian.DatabaseError,) as e: return msg(FX_ERROR_INDEX, _('Index error: %a'), e)

            if isinstance(ix_doc, xapian.Document):
                exists = True
                ix_doc.clear_terms()
                ix_doc.clear_values()
                uuid = ix_doc.get_data()
            else:
                exists = False
                ix_doc = xapian.Document()
                uuid = None
                    
            if uuid in (None, ''):
                # Generating UUID... A desperate fight against coincidence
                ts = datetime.now()
                uuid = f"""{int(round(ts.timestamp()))}{counter}{random_str(length=10)}{len(scast(self.vals['title'], str, 'a'))}"""
                ix_doc.set_data(uuid)



            self.DB.ixer.set_document(ix_doc)

            # Add UUID
            ix_doc.add_boolean_term(f"""UUID {uuid}""")
            # Add feed tag for easier deletes later on
            ix_doc.add_boolean_term(f'FEED_ID {self.vals["feed_id"]}')
            # ... and other filters
            ix_doc.add_boolean_term(f"""HANDLER {self.feed.get("handler",'')}""")
            if coalesce(self.vals["note"],0) >= 1: ix_doc.add_boolean_term(f"""NOTE 1""")
            else: ix_doc.add_boolean_term(f"""NOTE 0""")
            if coalesce(self.vals["read"],0) >= 1: ix_doc.add_boolean_term(f"""READ 1""")
            else: ix_doc.add_boolean_term(f"""READ 0""")

            ix_doc.add_value(0, xapian.sortable_serialise(scast(self.vals['pubdate'], int, 0)) )
            ix_doc.add_value(1, xapian.sortable_serialise(scast(self.vals['adddate'], int, 0)) )
            ix_doc.add_value(2, xapian.sortable_serialise(scast(self.vals['flag'], int, 0)) )

            # Index token strings, restarting term position after each one to facilitate mixed searches ...
            for k in ('',PREFIXES['exact'],):
                self.DB.ixer.set_termpos(0)
                for f in self.ix_strings[k]: self.DB.ixer.index_text( scast(f[1], str, ''), scast(f[0], int, 1), k)
            last_pos = self.DB.ixer.get_termpos() + 100
                
            # Add semantic postings one by one not to spam ...
            for f in self.ix_strings[PREFIXES['sem']]:
                sems = f[1]
                weight = scast(f[0], int, 1)
                for s,ps in sems.items():
                    for p in ps:
                        ix_doc.add_posting(f"""{PREFIXES['sem']}{s.lower()}""", p, weight)
    
            # Index meta fields
            self.DB.ixer.set_termpos(last_pos)
            for k in META_PREFIXES:
                for f in self.ix_strings[k]: self.DB.ixer.index_text( scast(f[1], str, ''), scast(f[0], int, 1), k)
            self.DB.ixer.set_termpos(last_pos)
            for k in META_PREFIXES_EXACT:
                for f in self.ix_strings[k]: self.DB.ixer.index_text( scast(f[1], str, ''), scast(f[0], int, 1), k)

            # Save stemming variants
            for k,v in self.DB.LP.variants.items():
                for s in v: self.DB.ixer_db.add_synonym(k,s)

            # Add/Replace in Database
            if exists:
                try: self.vals['ix_id'] = self.DB.ixer_db.replace_document(f'UUID {uuid}', ix_doc)
                except (xapian.DatabaseError, xapian.DocNotFoundError,) as e: 
                    return msg(FX_ERROR_INDEX, _('Index error: %a'), e)
                debug(2, f'Replaced Xapian doc: {self.vals["ix_id"]}')
            else:            
                try: self.vals['ix_id'] = self.DB.ixer_db.add_document(ix_doc)
                except (xapian.DatabaseError,) as e: 
                    return msg(FX_ERROR_INDEX, _('Index error: %a'), e)
                debug(2, f"""Added Xapian doc: {self.vals['ix_id']}""")




        if learn:
            # Learn text features by creating a learning string and running smallsem on it...
            self.learning_string = ''
            for f in LING_TEXT_LIST: self.learning_string = f"""{self.learning_string}  {scast(self.vals[f], str, '')}"""
            depth = kargs.get('learning_depth', MAX_FEATURES_PER_ENTRY)
            terms_tmp = self.DB.LP.extract_features(self.learning_string, depth=depth)


            model = self.DB.LP.get_model()

            self.terms.clear()
            for r in terms_tmp:
                self.term.clear()
                self.term['term'] = scast(r[2], str, '')
                self.term['weight'] = scast(r[1], float, 0) #* self.vals['weight']
                self.term['model'] = model
                self.term['form'] = scast(r[0], str, '')
                self.term['context_id'] = self.vals['id']

                self.terms.append(self.term.vals.copy())

            # Sometimes we need to temporarily skip saving terms to DB
            if save_terms:
                err = self.save_terms()
                if err != 0: return err
        
        return 0





    def save_terms(self, **kargs):
        """ Save pending learned terms """
        if fdx.debug_level in (1,4): 
            for r in self.terms: print(r)

        # ... delete existing keywords for this entry ...
        err = self.DB.run_sql_lock("delete from terms where context_id = :id", {'id': self.vals['id']} )
        if err != 0: return err

        # ... and save new keyword set to database
        err = self.DB.run_sql_lock(self.term.insert_sql(all=True), self.terms)
        if err != 0: 
            self.DB.last_term_id = self.DB.lastrowid
            return err

        debug(4, 'Keyword terms learned')
        return 0



    def summarize(self, level, **kargs):
        """ Summarize this entry """
        self.DB.connect_LP()
        self.DB.LP.summarize_entry(self.vals, level, **kargs)







    def __str__(self):
        ostring = SQLContainerEditable.__str__(self)
        terms = []
        try: ix_doc = self.DB.ix.get_document(self.vals['ix_id'])
        except (xapian.DatabaseError, xapian.DocNotFoundError) as e: ix_doc = None
        if isinstance(ix_doc, xapian.Document):
            for t in ix_doc.termlist(): terms.append(t.term.decode('utf-8')) 
        term_str = ''
        for t in terms: term_str = f"""{term_str}{t} """
        ostring = f"""{ostring}
-----------------------------------------------------------------------------------------------------------
{term_str}
"""
        return ostring
    


