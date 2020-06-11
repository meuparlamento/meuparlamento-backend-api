# -*- coding: utf-8 -*-

import re
from datetime import datetime

def parse_author_name(text):    
    name = text
    if("(" in text):
        name = text[:text.find("(")]
    return name.strip()

def parse_party_name(text):    
    party = ""
    if("(" in text):
        party = re.search('\((.*?)\)',text).group(1)   
    return party.strip()

def parse_original_document_url(url):
    try:
        https_indexes = [ (i.start(), i.end()) for i in re.finditer('http+', url)]
        return url[https_indexes[-1][0]:]
    except:
        return url

def decode_vote(party, row):
    if party in row["votos"]["afavor"]:
        return 1
    elif party in row["votos"]["contra"]:
        return -1
    elif party in row["votos"]["abstencao"]:
        return 0
    else:
        return None
    
def convert_doc_to_app_protocol(row):    
    
    doc = {
        "IDProposal":row["BID"],
        "Description":row["title"],
        "LinkPdf":row["pdfLink"],
        "VoteDate":datetime.fromtimestamp(row["dataVotacao"]/1000).strftime("%Y-%m-%d"),
        "VoteYear":row["anoVotacao"],
        "ProposedBy":row["proposedBy"],
        "url":row["url"],
        
        "Summary":row["metadata"]["proposal_summary"],
    }


    if(len(row["authors"]) > 0):
        doc["ProposedByAuthor"] = row["authors"][0]["name"]
        doc["ProposedByAuthorBioURL"] = row["authors"][0]["bioURL"]

    if("resultadoFinal" in row):
        doc["Result"] = row["resultadoFinal"]

        # assigned comissions
        doc["Comissions"] = row["comissoes"]

        # FIXME: support all parties    
        doc["PSD"] = decode_vote("PSD", row)
        doc["PS"] = decode_vote("PS", row)
        doc["CDS_PP"] = decode_vote("CDS_PP".replace("_","-"), row)
        doc["PCP"] = decode_vote("PCP", row)
        doc["BE"] = decode_vote("BE", row)
        doc["PEV"] = decode_vote("PEV", row)
        doc["PAN"] = decode_vote("PAN", row)

    # FIXME: solucao paliativa para o link dos documentos de propostas vinda do arquivo. 
    # ignora versao do arquivo e busca url original do pdf. tentar solucionar essa questao com o suporte do arquivo.pt             
    # TODO refactor this
    if("arquivo.pt" in doc["LinkPdf"]):            
        doc["LinkPdf"] = parse_original_document_url(doc["LinkPdf"])

    return doc