# -*- coding: utf-8 -*-

from chalicelib import utils

class TestUtils:
    def test_parse_author_name(self):    
        assert utils.parse_author_name("Arthur Filipe (PDT)") == "Arthur Filipe"

    def test_parse_party_name(self):    
        assert utils.parse_party_name("Arthur Filipe (PDT)") == "PDT"    

    def test_decode_vote(self):    
        votes = {"votos":{
            "afavor":"PS, PCP, VERDES",
            "abstencao":"CDS-PP, PSD",
            "contra":"PAN",
        }}

        assert utils.decode_vote("PCP",votes) == 1
        assert utils.decode_vote("PSD",votes) == 0
        assert utils.decode_vote("PAN",votes) == -1
        assert utils.decode_vote("PS",votes) == 1
