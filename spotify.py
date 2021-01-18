#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:38:05 2021

@author: lucas
"""
import base64
import requests
import datetime
from urllib.parse import urlencode
from openpyxl import Workbook
import client_info
client_id = client_info.client_id
client_secret = client_info.client_secret
# client_creds = f"{client_id}:{client_secret}"
# client_creds_b64 = base64.b64encode(client_creds.encode())
# # print(client_creds_b64)
# token_url = 'https://accounts.spotify.com/api/token'
# method = 'POST'
# token_data = {
#     "grant_type" : "client_credentials"
#     }
# token_headers = {
#     "Authorization" : f"Basic {client_creds_b64.decode()}" #<base64 encoded client_id:client_secret>
#     }

# r = requests.post(token_url, data = token_data, headers = token_headers)
# # print(r.json())
# valid_request = r.status_code_data in range(200, 299)
# if valid_request:
#     token_repsonse_data = r.json()
#     access_token = token_repsonse_data['access_token']
#     expires_in = token_repsonse_data['expires_in'] #seconds
#     now = datetime.datetime.now()
#     expires = now + datetime.timedelta(seconds=expires_in)
#     did_expires = expires < now
#     print(access_token,expires_in, did_expires)

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expires = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_client_creds_b64(self):
        """
        Return base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception('your must set client_id and client_secret')
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_headers(self):
        client_creds_b64 = self.get_client_creds_b64()
        
        return {
            "Authorization" : f"Basic {client_creds_b64}" #<base64 encoded client_id:client_secret>
            }
    
    def get_token_data(self):
        return {
            "grant_type" : "client_credentials"
            }
        
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        
        r = requests.post(token_url, data = token_data, headers = token_headers)
        # print(r.json())
        if r.status_code not in range(200, 299):
            raise Exception("Could not authorize client")
            # return False
        
        data = r.json()
        access_token = data['access_token']
        expires_in = data['expires_in'] #seconds
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expires = expires < now
        return True
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        # print(token)
        return token
    
    def get_access_headers(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization" : f"Bearer {access_token}"
            }
        return headers
    
    def search(self, query, search_type='artist'):
        headers = self.get_access_headers()
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": query, "type":search_type.lower()})
        lookup_url = f"{endpoint}?{data}"
        # print(lookup_url)
        r = requests.get(lookup_url, headers = headers)
        # print(r.status_code)
        # print(r.json())
        if r.status_code not in range(200,299):
            return {}
        return r.json()
    

    
    def get_list_playlist(self, userid, limit = 20, offset = 0): 
        base_url= 'https://api.spotify.com/v1/users/'
        endpoint = f'{base_url}{userid}/playlists?offset={offset}&limit={limit}'
        headers = self.get_access_headers()
        r = requests.get(endpoint, headers = headers)
        if r.status_code not in range(200,299):
            raise Exception('Connection Failed')
        
        my_playlist = r.json()
        # print(my_playlist['items'][1]['uri'])
        playlist_name = [i['name'] for i in my_playlist['items']] 
        playlist_url = [i['external_urls']['spotify'] for i in my_playlist['items']] 
        playlist_uri = [i['uri'][17:] for i in my_playlist['items']] 
        if my_playlist['next'] != None:
            playlist_name += self.get_list_playlist(userid, limit = 20, offset = offset + limit)[0]
            playlist_url += self.get_list_playlist(userid, limit = 20, offset = offset + limit)[1]
            playlist_uri += self.get_list_playlist(userid, limit = 20, offset = offset + limit)[2]
        return [playlist_name, playlist_url, playlist_uri]
    
    def get_playlist(self, userid):
        playlist = self.get_list_playlist(userid)
        total = len(playlist[0])
        
        for i in range(total):
            print(playlist[0][i], playlist[1][i], playlist[2][i], '\n')
        print(f"Total Playlist: {total}")
        # return playlist
    
    def get_playlist_songs(self, userid):
        
        #Excel
        wb = Workbook()
        
        base_url = 'https://api.spotify.com/v1/playlists/'
        headers = self.get_access_headers()
        list_playlist = self.get_list_playlist(userid)
        
        total = len(list_playlist[0]) #total numer of playlist
        # print(list_playlist)
        total_songs = {}
        for i in range(total):
            playlist_name = list_playlist[0][i]
            
            
            #excel sheet
            new = playlist_name.replace("[","")
            new2 = new.replace("]","")
            new3 = new2.replace("/","-")
            new4 = new3.replace("*","")
            new5 = new4.replace(":","")
            # print(new4)
            ws = wb.create_sheet(new5)
            
            playlist = list_playlist[2][i]
            endpoint = f'{base_url}{playlist}'
            # print(endpoint)
            r = requests.get(endpoint, headers = headers)
            content = []
            item = r.json()['tracks']['items']
            
            for i in item:
                try:
                    song_name = i['track']['name']
                    song_url = i['track']['external_urls']['spotify']
                    song_artist = i['track']['artists']
                except Exception:
                    pass
                artist = ""
                for c in song_artist:
                    artist += c['name']
                    artist += ','
                artist = artist[:-1]
                
                content.append(song_name)
                content.append(artist)
                content.append(song_url)
                total_songs[playlist_name] = content
                
                #excel
                ws.append([song_name,artist,song_url])
        
        wb.save('Spotify_Playlist.xlsx')
        return total_songs
            
            
        
        
        
    
spotify = SpotifyAPI(client_id, client_secret)
# search_result = spotify.search("Time", search_type = "track")
User_id = '11186472292'
# my_playlist = spotify.get_playlist(User_id)
playlist_song = spotify.get_playlist_songs(User_id)
# print(playlist_song)




        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
