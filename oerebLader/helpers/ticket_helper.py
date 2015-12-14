# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import oerebLader.helpers.config
import oerebLader.helpers.sql_helper

def get_open_tickets():
    config = oerebLader.helpers.config.get_config()
    open_tickets_sql = "select ticket.id, ticket.name, ticket.LIEFEREINHEIT, liefereinheit.name from ticket left join liefereinheit on ticket.LIEFEREINHEIT=liefereinheit.ID where ticket.STATUS=1 order by ticket.id"
    open_tickets = oerebLader.helpers.sql_helper.readSQL(config['OEREB_WORK']['connection_string'], open_tickets_sql)
    
    ticket_list = []
    
    for open_ticket in open_tickets:
        ticket_string = "%s (%s) -- %s (%s)" % (unicode(open_ticket[0]), open_ticket[1], open_ticket[3], unicode(open_ticket[2]))
        ticket_list.append(ticket_string)
        
    return ticket_list