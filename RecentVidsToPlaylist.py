import os
import re

from datetime import datetime
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

#The code is a  program which adds recent videos from channels a youtube user is subscibed to, to their selected playlist
#The program only adds videos uploaded on the day the program is run
#The program saves users time and allow them to conviniently access their favourite youtubers videos
#The program also benefits users as they can see videos added to the playlist uploaded from youtubers they may have forgotten they even subscribed to

class Youtube:
    def __init__(self):
        self.youtube_client = self.get_youtube_client()

    def get_youtube_client(self):
        """ Log Into Youtube, Copied from Youtube Data API """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "/Users/macbook/PycharmProjects/SpotifyProject/client_secret.json" #you will have to download your own youtube client_secret

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client



   #Method to get the current date and compare it to the uploaded videos date that is returned
    def get_current_date(self):
        date = self.format_date(str(datetime.now()))
        return date


   #The date published of each video returned from a channel is in an strange format and needs to be re-formatted
    def format_date(self,date):
        match = re.search(r'\d{4}-\d{2}-\d{2}', date)
        match = datetime.strptime(match.group(), '%Y-%m-%d').date()
        return match

#Method to get the channel Ids of the channels the user is subscribed to
    def subcription_channel_Ids(self):
        channel_Ids_list = []
        request = self.youtube_client.subscriptions().list(
            part="snippet, id",
            maxResults=100,
            mine = True

        )
        responses = request.execute()['items']
        for item in responses:
            channelId = item['snippet']['resourceId']['channelId']
            channel_Ids_list.append(channelId)


        return channel_Ids_list

    # This method returns the upload feeds Ids of each youtube channel the user is subscribed to
    def channel_uploads_Id(self):
        channel_Ids = self.subcription_channel_Ids()
        upload_Ids_list = []

        for channel_Id in channel_Ids:  #loop through each channel Ids to get their individual upload feed


            request = self.youtube_client.channels().list(
                part="contentDetails",
                maxResults=100,
                id=channel_Id

            )

            responses = request.execute()['items']
            for item in responses:
                uploads_Ids = item['contentDetails']['relatedPlaylists']['uploads']
                upload_Ids_list.append(uploads_Ids)  #The upload Id
            return upload_Ids_list


   #The upload feed Ids can be used to extract the videos uploaded on a channel
    def get_videos_from_uploads(self):
        latest_videos_Ids = []
        uploads_Ids = self.channel_uploads_Id()

        for upload_Id in uploads_Ids: #loop through each upload Ids to get the videos from each youtubers upload feed

            request = self.youtube_client.playlistItems().list(
                part="snippet",
                maxResults=10,  #ensures only 10 videos are returned, unlikely a youtube channel will upload more than that in a day
                playlistId=upload_Id

            )

            response = request.execute()['items']

            for item in response:
                getpublished = item['snippet']['publishedAt']
                if(self.format_date(getpublished)==self.get_current_date()): #comparing whether the videos returned are uploaded on the current date
                    latest_videos_Ids.append(item['snippet']['resourceId']['videoId'])  #if yes append their Ids to the list
            return latest_videos_Ids   #returning the list of videos


   #User choose which playlist they want to add songs to, unfortuntely their is no API that allows videos to be added straight to the watch-later playlist
    def get_playlists(self):

        request = self.youtube_client.playlists().list(
            part="id, snippet",
            maxResults=50,
            mine = True
        )
        response = request.execute()

        playlists  = {}
        for item in response['items']:
            id = item['id']
            title = item['snippet']['title']
            playlists[title] = id


        return playlists


      #With this method user chooses the playlist they want to add the video to and videos are then inserted
    def youtube_add_songs(self):

        youtube_playlists = self.get_playlists()
        video_Ids = self.get_videos_from_uploads()

        print("Below are the youtube playlists you can add to:")
        for keys in youtube_playlists.keys():
            print(keys)
        user_playlist_choice = input("Please enter the youtube playlist you want to add to:")
        if (youtube_playlists.get(user_playlist_choice)):
         youtube_playlist_id = youtube_playlists.get(user_playlist_choice)
         for video_Id in video_Ids:
            request = self.youtube_client.playlistItems().insert(
                part="snippet",
                body={
                    'snippet': {
                        'playlistId': youtube_playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_Id
                        }

                    }
                }

            )
            response = request.execute()
            print("adding recent videos from channels you subscribed to, to your selected playlist")
            print(response)










s= Youtube()
s.youtube_add_songs()

#Vague plan
# grab the youtubers channel ID
#place the channel ids in an array

#loop through each channel id and get the latest videos ids on the channel that was uploaded on the day

#The datetime appears in a sring fromat such as '2020-07-11T13:44:51Z', need to find a way to extract this


#add the first video to the youtubers watch later playlist

#maybe check all the users subcribers as it s unlikely most of them upload on the same day


#https://stackoverflow.com/questions/57104172/how-do-i-grab-the-date-that-a-channels-lastest-video-was-uploaded