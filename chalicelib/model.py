# -*- coding: utf-8 -*-

from random import shuffle
from datetime import datetime
import pymongo
import chalicelib.utils

# weigths should be in the database 
LIKELIHOOD_WEIGHT_GOVERNMENT = 0.6
LIKELIHOOD_WEIGHT_OPPOSITION = 0.4

class DataRepository(object):

    def __init__(self, config):
        self.config = config

    def connect(self):
        """Create database connection"""

        self.mongo_conn = pymongo.MongoClient(self.config["MONGODB_URI"], maxPoolSize=200 )
        self.db_name = self.config["DB_NAME"]

    def register_device(self, token):   
        """Save in the database device notification token"""

        self.mongo_conn[self.db_name]["notification_devices"].update_one({'token':token},
                                                                {'$set': {
                                                                    "token":token,
                                                                    "tstamp":datetime.now()
                                                                    }}, upsert=True)

    def find_authors_by_proposal_id(self, proposalID):
        """Return authors from proposal

        :proposalID: An integer, proposal's identifier
        """

        proposal = self.find_proposal_by_id(proposalID)
        authors = [] 

        if(proposal):
            
            for uid, item in enumerate(proposal["authors"]):
                
                author_name = chalicelib.utils.parse_author_name(item["name"]).strip()
                party_name = chalicelib.utils.parse_party_name(item["name"]).strip()
                
                hit = {
                    "title":author_name,
                    "domain":party_name,
                    "tstamp":int(datetime.fromtimestamp(proposal["dataVotacao"]/1000).strftime("%Y%m%d%H%M%S")),
                    "proposalID":proposalID,
                    "url":"https://arquivo.pt" + item["bioURL"],
                    "id":uid,
                    "type":"author"
                } 

                authors.append(hit)

        return authors

    def find_proposal_by_id(self, proposalID):
        """Return proposal

        :proposalID: An integer, proposal's identifier
        """
        return self.mongo_conn[self.db_name]["proposals"].find_one({"BID":int(proposalID)})
    
    def sampling_proposals(self, sample_size= 10, query = {}):
        """Return random proposals

        :sample_size: An integer, number of documents to return
        :query: A dictionary, query to filter documents
        """
        
        res = self.mongo_conn[self.db_name].command('aggregate', 'proposals', 
                                                    pipeline=[
                                                        {'$match': query }, 
                                                        {'$sort': { 'last_update': -1 } },
                                                        {'$sample': { 'size': sample_size } }
                                                    ], explain=False)
        return res['cursor']['firstBatch']

    def recent_batch(self, batch_size=10):
        """Return a batch with recent proposals

        :batch_size: An integer, max number of proposals to return
        """    
        
        query = {
            "metadata.num_chars":{"$lte":150}, 
            "metadata.readability_score": 0
            }
        
        recent_sampling = self.mongo_conn[self.db_name]["proposals"].find(query) \
                                                                    .sort([("dataVotacao",pymongo.DESCENDING)]) \
                                                                    .limit(batch_size)
        
        # convert proposals format
        final_sampling = [chalicelib.utils.convert_doc_to_app_protocol(row) for row in recent_sampling]
        
        return final_sampling

    def sampling_batch(self, batch_size=10):    
        """Return a batch with random proposals

        :batch_size: An integer, max number of proposals to return
        """    
        
        # compute number of government proposals for the batch
        government_balanced_likelihood = batch_size * LIKELIHOOD_WEIGHT_GOVERNMENT + 1

        # select random proposals authored by the government
        government_sampling = self.sampling_proposals(sample_size = government_balanced_likelihood, 
                                                        query = {
                                                        "metadata.is_governo":True, 
                                                        "metadata.readability_score": 0, 
                                                        "metadata.num_chars":{"$lte":150}
                                                        })

        # compute number of opposition proposals for the batch
        opposition_balanced_likelihood = batch_size * LIKELIHOOD_WEIGHT_OPPOSITION + 1

        # select random proposals authored by the oposition
        opposition_sampling = self.sampling_proposals(sample_size = opposition_balanced_likelihood,
                                                        query = {
                                                        "metadata.is_oposition":True, 
                                                        "metadata.readability_score": 0, 
                                                        "metadata.num_chars":{"$lte":150}
                                                        })

        # concat random proposals
        final_sampling = [chalicelib.utils.convert_doc_to_app_protocol(row) for row in government_sampling + opposition_sampling]
        
        # make sure the result set is shuffled
        shuffle(final_sampling)

        # limit batch size
        batch = final_sampling[0:batch_size]

        return batch

    def news_search(self, proposalID, proposalDate):
        """Return a list with related news websites

        :proposalID: An integer, proposal's identifier
        :proposalDate: proposal's vote date. Format "dd-mm-YYYY"
        """    

        news_domains_pt = [
            { "url":"http://expresso.pt/", "name": "Expresso"},    
            { "url":"http://publico.pt/", "name": "Público"},
            { "url":"http://www.dn.pt/", "name": "Diario de Noticias"},
            { "url":"http://www.jornaldenegocios.pt/", "name": "Jornal de Negócios"},
            { "url":"http://www.cmjornal.pt/", "name": "Correio da Manhã"},
        ]

        hits = [] 
        uid = 0

        proposalDate_plain_format = proposalDate.replace("-","") + "000000"
        for item in news_domains_pt:
            archive_news_url = "https://arquivo.pt/noFrame/replay/" + proposalDate_plain_format + "/" + item["url"]
            hit = {
                "title":item["name"],
                "domain":item["url"],
                "tstamp":int(proposalDate_plain_format),
                "proposalID":proposalID,
                "url":archive_news_url,
                "id":uid,
                "type":"news_outlet_homepage"
            } 
            uid+=1

            hits.append(hit)

        return hits