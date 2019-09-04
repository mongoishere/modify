import json, configparser, base64
import urllib.error
from urllib import request, parse

class Caller(object):

    def __init__(self):

        settings_file = configparser.ConfigParser()
        settings_file.read('config.ini')
        self.refresh_token = settings_file.get('Settings', 'refreshtoken')
        self.b64_profile = base64.b64encode(
            bytes(
                f"{settings_file.get('Settings', 'clientid')}:{settings_file.get('Settings', 'clientsecret')}"
            , 'utf-8')
        )

    def makeCall(self, endpoint_uri, auth_data, data=None, method=None, authorization='Bearer'):

        if(data):
            if(method == 'PUT'):
                put_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"{authorization} {auth_data}"
                }
                import requests; call_response = requests.put(endpoint_uri, data=json.dumps(data), headers=put_headers)
                #call_request = request.Request(endpoint_uri, call_data, method='PUT')
            else:
                call_data = parse.urlencode(data).encode()
                call_request = request.Request(endpoint_uri, call_data)
                
                try:
                    call_request.add_header('Authorization', f"{authorization} {auth_data}")
                    call_response = request.urlopen(call_request).read()

                except urllib.error.HTTPError as e: print(str(e.readlines()))
                #import pdb; pdb.set_trace(header="makeCall 1")

        else:
            call_request = request.Request(endpoint_uri)
            call_request.add_header('Authorization', f"{authorization} {auth_data}")
            call_response = request.urlopen(call_request).read()

        bytesObject = isinstance(call_response, bytes)
        if bytesObject: return(call_response.decode())
        else:  return(call_response)


    def retrieveToken(self, code):

        token_url="https://accounts.spotify.com/api/token"
        
        tokenReq_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://example.com"
        }

        retrieveToken_resp = self.makeCall(token_url, self.b64_profile.decode(), tokenReq_data,  authorization='Basic')
        retrieveToken = json.loads(retrieveToken_resp)['access_token']
        
        return(retrieveToken)

    def refreshToken(self):

        token_url="https://accounts.spotify.com/api/token"

        tokenReq_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token 
        }

        refreshToken_resp = self.makeCall(token_url, self.b64_profile.decode(), tokenReq_data, authorization='Basic')
        accessToken = json.loads(refreshToken_resp)['access_token']
        return(accessToken)