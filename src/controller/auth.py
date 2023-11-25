from datetime import datetime

from authomatic.adapters import WerkzeugAdapter
from authomatic.core import Authomatic
from authomatic.providers import oauth1, oauth2
from flask.globals import current_app, request
from flask.helpers import make_response
from flask.views import MethodView
from flask_security.forms import ResetPasswordForm
from flask_security.utils import hash_password

from controller.main import render
from model.main import User, get
from util.db import store

# @see https://stackoverflow.com/a/21987075
auth = Authomatic(config={'google': {
    'class_': oauth2.Google,
    'consumer_key': current_app.config.get('GOOGLE_API_CLIENT_ID'),
    'consumer_secret': current_app.config.get('GOOGLE_API_CLIENT_SECRET'),
    'scope': oauth2.Google.user_info_scope + ['https://gdata.youtube.com'],
}, 'tw': {
    'class_': oauth1.Twitter,
    'consumer_key': current_app.config.get('TWITTER_API_CLIENT_ID'),
    'consumer_secret': current_app.config.get('TWITTER_API_CLIENT_SECRET'),
}}, secret=current_app.config.get('SECRET_KEY'))


class Auth(MethodView):
    @staticmethod
    def get(provider_name):
        response = make_response()

        # Authenticate the user
        result = auth.login(adapter=WerkzeugAdapter(request=request, response=response),
                            provider_name=provider_name)
        if result:
            statuses = []
            tweets = []
            videos = []
            if result.user:
                # Get user info
                result.user.update()

                user = get(model=User, email=result.user.email)
                if user:
                    is_new = False
                    user.fs_uniquifier = result.user.id
                else:
                    user = User(active=True, email=result.user.email, fs_uniquifier=result.user.id)
                    is_new = True

                user.first_name = result.user.first_name
                user.last_name = result.user.last_name
                user.provider = provider_name

                store.put(user)
                store.commit()

                if result.user.credentials:
                    # Talk to Facebook API
                    if provider_name == 'fb':
                        response = result.provider.access('https://graph.facebook.com/{0}?fields=feed.limit(5)'.format(result.user.id))
                        if response.status == 200 and response.data.feed.data:
                            for status in response.data.feed.data:
                                statuses.append({'date': status.created_time, 'message':
                                                status.message or status.name or status.story})
                    # Talk to Google YouTube API
                    elif provider_name == 'google':
                        response = result.provider.access('https://gdata.youtube.com/'
                                                          'feeds/api/users/default/playlists?alt=json')
                        if response.status == 200:
                            videos = response.data.get('feed', {}).get('entry', [])
                    # Talk to Twitter API
                    elif provider_name == 'tw':
                        response = result.provider.access('https://api.twitter.com/1.1/statuses/user_timeline.json?count=5')
                        if response.status == 200 and response.data:
                            for tweet in response.data:
                                tweets.append({'date': tweet['created_at'], 'text': tweet['text']})

                return render(template_name_or_list='auth.html',
                              user=user,
                              is_new=is_new,
                              set_password_form=ResetPasswordForm(),
                              facebook_statuses=statuses,
                              twitter_tweets=tweets,
                              youtube_videos=videos)
        return response

    @staticmethod
    def post(provider_name):
        user = User.query.get(int(request.form.get(key='user_id')))
        form = ResetPasswordForm(request.form)

        if form.validate():
            user.confirmed_at = datetime.now()
            user.password = hash_password(request.form.get(key='password'))

            store.put(user)
            store.commit()

            return render(template_name_or_list='auth.html',
                          user=user,
                          is_new=request.form.get(key='is_new'))
        return render(template_name_or_list='auth.html',
                      user=user,
                      is_new=request.form.get(key='is_new'),
                      set_password_form=form)
