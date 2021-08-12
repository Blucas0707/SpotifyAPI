# SpotifyAPI

### 目的
利用Spotify API，取得自己的帳戶音樂分類及曲目。

### 流程
1. 先申請自己的client_id & client_secret_key，並存到client_info.py中
2. 利用client_id & client_secret_key 去取得access_token 並記錄expire_time
3. 用access_token 去做出access_header authorization格式，若access_token過期，則重新送出申請，取得新的access_token & expire time
4. 之後就可以用此access_header authorization格式去對API送出request, ex: search、users等
 
