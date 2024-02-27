import io, sys, os
import base64
import re
import hashlib
import requests
import random
import string
import html
import urllib3
import urllib.parse
import logging
import socket
from typing import Any
from ..utils import Parser

class HaloProxy(object):
    def __init__(self, username, password, logger=None):
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.__url = "https://halo.cancer.gov/"
        self.__auth_path = "/idsrv/connect/authorize"
        self.__login_path = "/idsrv/connect/token"
        self.__api_path = "/graphql"
        self.__verify = False
        self.__session = requests.Session()
        self.__credentials = { "username": username,
                               "password": password }
        self.authorization_code_login(self.__credentials, "authorization_code")

    def execute(self, query: str, variables: str = None, op_name: str = None, throw_error: bool = True):
        query_endpoint = urllib.parse.urljoin(self.__url, self.__api_path)
        request = {
            'query': query.strip(),
            'variables': variables or dict(),
            'operationName': op_name,
        }
        response = self.__session.post(
            url=query_endpoint,
            json=request,
            verify=self.__verify
        )
        payload = Parser.str_to_obj(response.text)
        if hasattr(payload, "errors") and payload.errors:
            message = Parser.dict_to_str({
                "message": [err.message for err in payload.errors],
                "input": request
            })
            raise Exception(message)
        data = self.__result_parser(payload.data[0])
        return data
    def getAnn(self, id):
        htmlString = self.execute(query='''
            query($imgId: String) {
              images (query: {
                where: {
                  q: {
                    f: "tag"
                    pred: {
                      op: CONTAINS
                      v: $imgId
                    }
                  }
                }
              }) {
                edges {
                  node {
                    id
                    location
                    annotationLayers {
                      id
                      name
                      color
                      regions {
                        pk
                        hasEndcaps
                        shapeType
                        geometry
                        isExclusionRegion
                      }
                    }
                  }
                }
              }
            }
            ''',
            variables={
                'imgId': id # config.input.image_id,
            })

        return htmlString

    def authorization_code_login(self, credentials: dict, grant_type: str):
        # Finds unbound port for OIDC redirect
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]

        # Pre installed OIDC variables
        client_id = "halo"
        redirect_uri = f"http://127.0.0.1:{port}"

        # PKCE code verifier and challenge
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
        code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)
        code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
        code_challenge = code_challenge.replace('=', '')


        # Request login page
        state = ''.join(random.choice(string.printable) for i in range(30))
        request = requests.Request(
            method='GET',
            url=urllib.parse.urljoin(self.__url, self.__auth_path),
            params={
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid profile graphql",
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            }
        )
        prepped = self.__session.prepare_request(request)
        response1 = self.__session.send(prepped,
            allow_redirects=False,
            verify=self.__verify)
        response1_1 = self.__session.send(response1.next,
            verify=self.__verify)

        # Parse login page for RequestVerificationToken
        page = response1_1.text
        request_token = html.unescape(re.search('<input\s+.*?\s+value="(.*?)"', page, re.DOTALL).group(1))

        # Parse response header for Antiforgery token
        cookie = response1_1.headers['Set-Cookie']
        cookie = '; '.join(c.split(';')[0] for c in cookie.split(', '))

        # Send user login credentials
        request2 = requests.Request(
            method='POST',
            url=response1_1.url,
            data={
                "__RequestVerificationToken": request_token,
                "scheme": "ldap",
                "username": credentials["username"],
                "password": credentials["password"],
            },
            headers={"Cookie": cookie}
        )
        prepped2 = self.__session.prepare_request(request2)
        response2 = self.__session.send(prepped2,
            allow_redirects=False,
            verify=self.__verify)
        if response2.is_redirect:
            response2_1 = self.__session.send(response2.next,
                allow_redirects=False,
                verify=self.__verify)
        else:
            raise Exception("login failed")

        # Parse redirect url for authentication code
        redirect = response2_1.next.url
        query = urllib.parse.urlparse(redirect).query
        redirect_params = urllib.parse.parse_qs(query)
        auth_code = redirect_params['code'][0]

        # Exchange authorization code for an access token
        request3 = requests.Request(
            method='POST',
            url=urllib.parse.urljoin(self.__url, self.__login_path),
            data={
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code": auth_code,
                "code_verifier": code_verifier,
                "grant_type": grant_type,
            }
        )
        prepped3 = self.__session.prepare_request(request3)
        response3 = self.__session.send(prepped3,
            allow_redirects=False,
            verify=self.__verify)

        # Update session header with bearer token
        data = Parser.str_to_obj(response3.text)
        self.__session.headers.update({
            "authorization": "bearer {}".format(data.access_token)
        })

    def __result_parser(self, data: Any):
        # Handles a list of items
        if hasattr(data, "edges"):
            return Parser.obj_to_dict([item.node for item in data.edges])

        # Handles result set data
        result_set = {}
        if hasattr(data, "collection"):
            result_set["collection"] = Parser.obj_to_dict([item.node for item in data.collection])
        if hasattr(data, "deleted"):
            result_set["deleted"] = Parser.obj_to_dict([item.node for item in data.deleted])
        if hasattr(data, "failed"):
            result_set["failed"] = Parser.obj_to_dict([item.node for item in data.failed])
        if hasattr(data, "mutated"):
            result_set["mutated"] = Parser.obj_to_dict([item.node for item in data.mutated])
        if result_set:
            return Parser.obj_to_dict(result_set)