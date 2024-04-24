from pusher import Pusher

# Initialize Pusher client
pusher_client = Pusher(
    app_id='your_app_id',
    key='your_app_key',
    secret='your_app_secret',
    cluster='your_app_cluster',
    ssl=True
)

def notify_client(transcript, score, magnitude):
    pusher_client.trigger('audio-channel', 'new-analysis', {
        'transcript': transcript,
        'score': score,
        'magnitude': magnitude
    })