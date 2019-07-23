# -*- coding: utf-8 -*-

import json
import gzip
import os
import logging 
from datetime import datetime

from chalice import Chalice, Response, BadRequestError
from chalicelib.model import DataRepository

# load environment variables
config = {
    "MONGODB_URI": os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
    "DB_NAME" : os.environ.get("DB_NAME", "meuParlamento")
}

# setup rest api app
app = Chalice(app_name='meuparlamento-backend-api')
app.api.binary_types.append('application/json')
app.log.setLevel(logging.DEBUG)

# setup data connections
data_repo = DataRepository(config)
data_repo.connect()

@app.route('/')
def index():
    """
    Test endpoint.
    Just to make sure it is running.
    """

    return {'hello': 'meuParlamento!'}

@app.route('/register_device', methods=["POST"])
def register_device():
    """
    Register unique id in order to send notifications.
    """

    app.log.debug("register nofitication device")

    try:
        # read request body
        request_body = app.current_request.json_body    

        if(request_body):
            data_repo.register_device(request_body['token'])

            return Response(status_code=201, 
                            body={"message":"Device registered for notification"},
                            headers={'Content-Type': 'application/json'})

    except  Exception as e:
        app.log.error("failed to register notification device")
        raise BadRequestError('Failed to register device. Unable to support notifications for this device')

@app.route('/proposals/batch/{batch_size}')
def generate_proposals_sampling(batch_size):
    """Return a batch with random proposals

    :batch_size: An integer, max number of proposals to return
    """    

    app.log.debug("get random proposals batch. size {}".format(batch_size))

    try:
        # generate sampling
        my_batch = data_repo.sampling_batch(int(batch_size))

        response = json.dumps({"data":my_batch}).encode('utf-8')
        payload = gzip.compress(response)
        return Response(status_code=200,
                        body=payload,
                        headers={'Content-Type': 'application/json',
                                'Content-Encoding': 'gzip'})
    except Exception as e:
        app.log.error("failed to get proposals batch")
        raise BadRequestError('Oops. Something bad happened :( If error persists, please contact system admin')

@app.route('/proposals/authors/{proposalID}')
def authors_from_proposal(proposalID):
    """Return authors from proposal

    :proposalID: An integer, proposal's identifier
    """

    app.log.debug("authors_from_proposal: {}".format(proposalID))

    try:
        authors = data_repo.find_authors_by_proposal_id(proposalID)
        
        response = json.dumps({"data":authors}).encode('utf-8')
        payload = gzip.compress(response)
        return Response(status_code=200,
                        body=payload,
                        headers={'Content-Type': 'application/json',
                                'Content-Encoding': 'gzip'})

    except Exception as e:
        app.log.error("failed to get authors from proposal {}".format(proposalID))
        raise BadRequestError('Oops. Something bad happened :( If error persists, please contact system admin')

@app.route('/proposals/news/{proposalID}')
def news_search(proposalID):
    """Return a list with related news websites

    :proposalID: An integer, proposal's identifier
    """    
    proposal = data_repo.find_proposal_by_id(proposalID)
    
    if(proposal):
        voteDate = datetime.fromtimestamp(proposal["dataVotacao"]/1000).strftime("%Y-%m-%d")
        return _news_search(proposalID, voteDate)

@app.route('/proposals/news/{proposalID}/{proposalDate}')
def _news_search(proposalID, proposalDate):
    """Return a list with related news websites

    :proposalID: An integer, proposal's identifier
    :proposalDate: proposal's vote date. Format "YYYY-mm-dd"
    """    

    app.log.debug("news_search: {}".format(proposalID))
    
    try: 
        hits = data_repo.news_search(proposalID, proposalDate)

        response = json.dumps({"data":hits}).encode('utf-8')
        payload = gzip.compress(response)
        return Response(status_code=200,
                        body=payload,
                        headers={'Content-Type': 'application/json',
                                'Content-Encoding': 'gzip'})
    
    except Exception as e:
        app.log.error("failed to search news from proposal id {} at {}".format(proposalID, proposalDate))
        raise BadRequestError('Oops. Something bad happened :( If error persists, please contact system admin')

