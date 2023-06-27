# -*- coding: utf-8 -*-
""" GUI classes for FEEDEX """

from feedex_gui_utils import *




class ResultGUIFeed(ResultFeed, ResultGUI):
    def __init__(self,  **kargs):
        ResultFeed.__init__(self, replace_nones=True, **kargs)
        ResultGUI.__init__(self, **kargs)
        self.gui_fields = ('id', 'gui_icon', 'name', 'name_mu', 'handler', 'gui_color', 'gui_weight', 'gui_action', 'gui_row_id')
        self.gui_types = (int, GdkPixbuf.Pixbuf,  str, str,   str,   str, int,  int,   str)





class FeedexFeedTab(Gtk.ScrolledWindow):
    """ Singleton for feed selection in GUI """


    def __init__(self, parent, *args, **kargs):

        # Maint. stuff
        self.MW = parent
        self.config = self.MW.config

        # GUI init
        Gtk.ScrolledWindow.__init__(self)
        
        # Value for scrollbar state
        self.vadj_val = 0
        self.expanding = False # Is operation expanding/collapsin nodes?


        # Flags and changeable params
        self.feed_sums = {}
        self.selected_feed_id = None
        self.selected_place = None

        # Buffer for copying a feed
        self.copy_selected = {'id':None, 'name':None, 'is_category':None}

        # Container for selected feed
        self.feed = ResultGUIFeed(main_win=self.MW)

        # Feed Tree
        self.feed_store = Gtk.TreeStore(*self.feed.gui_types)
        self.feed_store_tmp = Gtk.TreeStore(*self.feed.gui_types)
        self.feed_tree = Gtk.TreeView(model=self.feed_store)

        self.feed_tree.append_column( f_col(None, 3, self.feed.gindex('gui_icon'), resizable=False, clickable=False, width=16, reorderable=False) )
        self.feed_tree.append_column( f_col(None, 1, self.feed.gindex('name_mu'), clickable=False, reorderable=False, color_col=self.feed.gindex('gui_color')) )
        self.feed_tree.set_headers_visible(False)
        
        self.feed_tree.set_tooltip_markup(_("""These are available <b>Places</b>, <b>Channels</b> and <b>Categories</b>
Double-click on a place to quickly load entries  
Double-click on feed or category to filter results by chosen item
Right click for more options
Hit <b>Ctrl-F</b> for interactive search""") )

        self.selection = self.feed_tree.get_selection()

        self.feed_tree.connect("row-activated", self._on_activate_feed)
        self.feed_tree.connect("row-expanded", self._on_feed_expanded)
        self.feed_tree.connect("row-collapsed", self._on_feed_collapsed)
        self.feed_tree.connect("button-press-event", self._on_button_press)
        self.feed_tree.connect('size-allocate', self._tree_changed)

        self.feed_tree.set_enable_search(True)
        self.feed_tree.set_search_equal_func(self.MW.quick_find_case_ins_tree, self.feed_tree, self.feed.gindex('name'))
 
        self.feed_tree.set_enable_tree_lines(True)
        self.feed_tree.set_level_indentation(20)

        self.add(self.feed_tree)
        self.reload(load=False)





    def _on_button_press(self, widget, event):
        """ Launch action menu from main window """
        if event.button == 3:
            item = self.get_selection()
            if item is not None and item.gget('gui_action') == 0: 
                item.populate(fdx.find_f_o_c(item.gget('id'), load=True))
                self.MW.action_menu(item, self, event)





    def _on_activate_feed(self, *args):
        """ Activate feed/action """
        item = self.get_selection()
        if item is None: return -1

        # Filtering of current tab
        gaction = item.gget('gui_action')
        if gaction == 0:
            if isinstance(self.MW.curr_upper.table.result, (ResultEntry, ResultContext,)):
                item.populate(fdx.find_f_o_c(item.gget('id'), load=True))
                if coalesce(item['is_category'],0) == 0: ids = item['id']
                else:
                    ids = [item['id']]
                    for f in fdx.feeds_cache:
                        if coalesce(f[self.feed.get_index('parent_id')]) == item['id']: ids.append(f[self.feed.get_index('id')])
                self.MW.curr_upper.on_filter_by_feed(ids)

        # Going to places (1st tab)
        elif gaction == 1:
            for i in range(self.MW.upper_notebook.get_n_pages()):
                tab = self.MW.upper_notebook.get_nth_page(i)
                if tab is None: continue

                if tab.type == FX_TAB_PLACES:
                    place = item.gget('id')
                    tab.query(place, {})
                    self.MW.upper_notebook.set_current_page(i)
                    self.MW.curr_place = place
                    break

        # Filtering by handlers
        elif gaction == 2:
            if isinstance(self.MW.curr_upper.table.result, (ResultEntry, ResultContext,)):
                ids = []
                for f in fdx.feeds_cache:
                    if f[self.feed.get_index('handler')] == item.gget('handler'): ids.append(f[self.feed.get_index('id')])
                self.MW.curr_upper.on_filter_by_feed(ids)




    def get_selection(self, *args):
        """ Loads feed from selection to container """
        model, treeiter = self.selection.get_selected()
        if treeiter is not None:
            self.feed.gpopulate(list(model[treeiter]))
            debug(7, f'Selected feed: {self.feed.gget("id")}')
            return self.feed





    def _on_feed_expanded(self, *args):
        """ Register expanded rows """
        path = args[-1]
        id = self.feed_store[path][self.feed.gindex('gui_row_id')]
        self.MW.gui_cache['feeds_expanded'][str(id)] = True
        self.expanding = True

    def _on_feed_collapsed(self, *args):
        """ Register collapsed rows """
        path = args[-1]
        id = self.feed_store[path][self.feed.gindex('gui_row_id')]
        self.MW.gui_cache['feeds_expanded'][str(id)] = False
        self.expanding = True







    def copy_feed(self, *args, **kargs):
        """ Copy feed/category to buffer """
        item = self.get_selection()
        if item is None: return -1
        if item.gget('gui_action') != 0: return -1
        self.copy_selected = {'id':item['id'], 'name': item.name(), 'is_category': item.get('is_category',0)}
        msg(_('%a selected for moving...'), self.copy_selected['name'])

    def insert_feed(self, *args, **kargs):
        """ Insert feed in-place"""
        target = args[-1]
        if target is None: return -1
        if target.gget('gui_action') != 0: return -1
        item = FeedexFeed(self.MW.DB, id=self.copy_selected['id'])
        #item = item.convert(FeedexFeed, self.MW.DB, id=item['id'])
        err = item.order_insert(target.get('id'), with_cat=True)
        if err == 0:
            self.copy_selected.clear()
            self.reload()











    def _feed_store_item(self, item):
        """ Generates a list of feed fields """
        tp = type(item)
        if tp in (list, tuple):
            self.feed.clear()
            self.feed.gclear()
            self.feed.populate(item)
        elif tp is dict:
            self.feed.clear()
            self.feed.gclear()
            self.feed.gui_vals = item.copy()
        elif item is None:
            self.feed.gclear()
            self.feed.gui_vals['gui_action'] = -1
            return self.feed.gtuplify()
        else: return None

        
        if self.feed.gget('gui_action') in (0, None):
            
            self.feed.gui_vals['id'] = self.feed['id']

            self.feed.gui_vals['gui_action'] = 0
            self.feed.gui_vals['name'] = esc_mu(self.feed.name())
            self.feed.gui_vals['name_mu'] = self.feed.gui_vals['name']

            if coalesce(self.feed.get('error'),0) >= self.config.get('error_threshold',5):
                self.feed.gui_vals['gui_icon'] = self.MW.icons.get('error', None)
                self.feed.gui_vals['gui_color'] = 'red'

            elif coalesce(self.feed.get('deleted'),0) == 1:
                if coalesce(self.feed.get('is_category'),0) == 1:
                    self.feed.gui_vals['gui_icon'] = self.MW.icons.get(self.feed["id"], self.MW.icons.get('doc',None))
                else:
                    self.feed.gui_vals['gui_icon'] = self.MW.icons.get(self.feed["id"], self.MW.icons.get('default',None))
                self.feed.gui_vals['gui_color'] = self.config.get('gui_deleted_color','grey')

            else:
                self.feed.gui_vals['gui_icon'] = self.MW.icons.get(self.feed["id"], self.MW.icons.get('default',None))
                self.feed.gui_vals['gui_color'] = None

            self.feed.gui_vals['gui_row_id'] = f"""FoC {self.feed['id']}"""


        else:
            self.feed.gui_vals['name'] = esc_mu(self.feed.gui_vals['name'])
            self.feed.gui_vals['name_mu'] = self.feed.gui_vals['name']
            if self.feed.gui_vals.get('gui_icon') not in (None, ''): self.feed.gui_vals['gui_icon'] = self.MW.icons.get(self.feed.gui_vals["gui_icon"], self.MW.icons.get('default',None))
            self.feed.gui_vals['gui_color'] = None
        
        return self.feed.gtuplify()








    def _redecorate(self, model, path, iter, *args):
        """ Check redecorate for each tree node """
        sums = args[-1]
        filters = args[-2]
        main_filter = args[-3]

        if model[iter][self.feed.gindex('gui_action')] == 0:
            id = model[iter][self.feed.gindex('id')]
            name = model[iter][self.feed.gindex('name')]
            if sums.get(id, 0) > 0: model[iter][self.feed.gindex('name_mu')] = f"""<b>{name} ({sums.get(id, 0)})</b>"""
            else: model[iter][self.feed.gindex('name_mu')] = name

            if id == main_filter or id in filters: model[iter][self.feed.gindex('name_mu')] = f"""<u>{model[iter][self.feed.gindex('name_mu')]}</u>"""

        if self.MW.curr_upper.type == FX_TAB_PLACES:
            if model[iter][self.feed.gindex('gui_action')] == 1:
                if model[iter][self.feed.gindex('id')] == self.MW.curr_place:
                    model[iter][self.feed.gindex('name_mu')] = f"""<u><b>{model[iter][self.feed.gindex('name')]}</b></u>"""
                else: model[iter][self.feed.gindex('name_mu')] = model[iter][self.feed.gindex('name')]
        return False


    def redecorate(self, filter, sums):
        """ Change decorations (match number and underlining)"""
        self.feed_sums = sums.copy()
        filters = scast(filter, tuple, ())
        main_filter = slist(filters, 0, None)

        if self.feed_sums in (None, {}): return 0

        self.feed_store.foreach(self._redecorate, main_filter, filters, self.feed_sums)






    def reload(self, *args, **kargs):
        """ Loads feed data and entry types (inverse id) into list store """

        if kargs.get('load',True):
            self.MW.DB.load_icons()
            self.MW.icons = get_icons(fdx.feeds_cache, fdx.icons_cache)

        adj = self.feed_tree.get_vadjustment()
        self.vadj_val = adj.get_value()

        expanded = []
        self.feed_store_tmp.clear()

        # Update store ...
        # Places tree ...
        new_row = self.feed_store_tmp.append(None, self._feed_store_item({'gui_action':1, 'name':_('New'), 'gui_icon':'new', 'id':FX_PLACE_LAST, 'gui_row_id':'P 1'}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('Previous Update'), 'gui_icon':'calendar', 'id':FX_PLACE_PREV_LAST}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('Last Hour'), 'gui_icon':'calendar', 'id':FX_PLACE_LAST_HOUR}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('Today'), 'gui_icon':'calendar', 'id':FX_PLACE_TODAY}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('This Week'), 'gui_icon':'calendar', 'id':FX_PLACE_LAST_WEEK}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('This Month'), 'gui_icon':'calendar', 'id':FX_PLACE_LAST_MONTH}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('This Quarter'), 'gui_icon':'calendar', 'id':FX_PLACE_LAST_QUARTER}) )
        self.feed_store_tmp.append(new_row, self._feed_store_item({'gui_action':1, 'name':_('Last Six Month'), 'gui_icon':'calendar', 'id':FX_PLACE_LAST_SIX_MONTHS}) )

        if self.MW.gui_cache.get('feeds_expanded',{}).get('P 1',False): expanded.append(new_row)


        self.feed_store_tmp.append(None, self._feed_store_item(None))

        # Grouped by categories ...
        for c in fdx.feeds_cache:

            if c[self.feed.get_index('is_category')] != 1: continue
            if c[self.feed.get_index('deleted')] == 1: continue
            id = c[self.feed.get_index('id')]
            cat_row = self.feed_store_tmp.append(None, self._feed_store_item(c))

            for f in fdx.feeds_cache:
                if f[self.feed.get_index('parent_id')] == id and f[self.feed.get_index('is_category')] != 1 and coalesce(f[self.feed.get_index('deleted')],0) == 0:
                    self.feed_store_tmp.append(cat_row, self._feed_store_item(f))

            if self.MW.gui_cache.get('feeds_expanded',{}).get(f"FoC {c[self.feed.get_index('id')]}",False): expanded.append(cat_row)
        

        self.feed_store_tmp.append(None, self._feed_store_item(None))

        # Crouped by handler type ...
        rss_row = self.feed_store_tmp.append(None, self._feed_store_item({'gui_action':2, 'name':_('RSS'), 'gui_icon':'rss', 'handler':'rss', 'gui_row_id':'H rss'}))
        for f in fdx.feeds_cache:
            if f[self.feed.get_index('deleted')] != 1 and f[self.feed.get_index('is_category')] != 1 and f[self.feed.get_index('handler')] == 'rss':
                self.feed_store_tmp.append(rss_row, self._feed_store_item(f))
        if self.MW.gui_cache.get('feeds_expanded',{}).get('H rss',False): expanded.append(rss_row)

        html_row = self.feed_store_tmp.append(None, self._feed_store_item({'gui_action':2, 'name':_('HTML'), 'gui_icon':'www', 'handler':'html', 'gui_row_id':'H html'}))
        for f in fdx.feeds_cache:
            if f[self.feed.get_index('deleted')] != 1 and f[self.feed.get_index('is_category')] != 1 and f[self.feed.get_index('handler')] == 'html':
                self.feed_store_tmp.append(html_row, self._feed_store_item(f))
        if self.MW.gui_cache.get('feeds_expanded',{}).get('H html',False): expanded.append(html_row)

        script_row = self.feed_store_tmp.append(None, self._feed_store_item({'gui_action':2, 'name':_('Script'), 'gui_icon':'script', 'handler':'script', 'gui_row_id':'H script'}))
        for f in fdx.feeds_cache:
            if f[self.feed.get_index('deleted')] != 1 and f[self.feed.get_index('is_category')] != 1 and f[self.feed.get_index('handler')] == 'script':
                self.feed_store_tmp.append(script_row, self._feed_store_item(f))
        if self.MW.gui_cache.get('feeds_expanded',{}).get('H script',False): expanded.append(script_row)

        local_row = self.feed_store_tmp.append(None, self._feed_store_item({'gui_action':2, 'name':_('Local'), 'gui_icon':'disk', 'handler':'local', 'gui_row_id':'H local'}))
        for f in fdx.feeds_cache:
            if f[self.feed.get_index('deleted')] != 1 and f[self.feed.get_index('is_category')] != 1 and f[self.feed.get_index('handler')] == 'local':
                self.feed_store_tmp.append(local_row, self._feed_store_item(f))
        if self.MW.gui_cache.get('feeds_expanded',{}).get('H local',False): expanded.append(local_row)



        self.feed_store_tmp.append(None, self._feed_store_item(None))

        # Trash bin items...
        trash_row = self.feed_store_tmp.append(None, self._feed_store_item({'gui_action':1, 'name':_('Trash Bin'), 'gui_icon':'trash', 'id':FX_PLACE_TRASH_BIN, 'gui_row_id':'TB'}) )        
        for f in fdx.feeds_cache:
            if f[self.feed.get_index('deleted')] == 1:
                self.feed_store_tmp.append(trash_row, self._feed_store_item(f))
        if self.MW.gui_cache.get('feeds_expanded',{}).get('TB',False): expanded.append(trash_row)



        # Apply store to view
        self.feed_store = self.feed_store_tmp
        self.feed_tree.set_model(self.feed_store)
        # ... and expand relevant rows
        for e in expanded: self.feed_tree.expand_row(self.feed_store.get_path(e), False)
        self.expanding = False

        if self.MW.curr_upper is not None:
            self.redecorate(self.MW.curr_upper.table.curr_feed_filters, self.MW.curr_upper.table.feed_sums)



    def _tree_changed(self, *args, **kargs):
        if not self.expanding:
            adj = self.feed_tree.get_vadjustment()
            adj.set_value(self.vadj_val)








