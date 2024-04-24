from pusher import Pusher

# Initialize Pusher client
pusher_client = Pusher(
    app_id='1792935',
    key='20f7d6caed6b5edf6072',
    secret='ef5254e7091bc69f34b8',
    cluster='ap2',
    ssl=True
)

def notify_client(transcript, score, magnitude):
    pusher_client.trigger('audio-channel', 'new-analysis', {
        'transcript': transcript,
        'score': score,
        'magnitude': magnitude
    })