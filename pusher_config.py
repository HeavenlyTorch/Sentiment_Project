from pusher import Pusher

# Initialize Pusher client
pusher_client = Pusher(
    app_id='d8e7f8f7-23e3-4425-b037-29c66b684d99',
    key='FFF21819C019D9082ED407D94789D2B91820B2EEEB13571481502785C1259E2E',
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