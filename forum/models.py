from django.db import models

_max_length = 200


class UserData(models.Model):
    username = models.CharField(max_length=_max_length)
    confirming_token = models.CharField(max_length=_max_length)
    is_confirmed = models.BooleanField()

    def __str__(self):
        return 'KUser[username: {}, email: {}, is_confirmed: {}]'.format(self.username, self.email, self.is_confirmed)


class Message(models.Model):
    message_text = models.CharField(max_length=_max_length)
    publication_date = models.DateTimeField('publication date')
    topic_id = models.IntegerField()
    message_id = models.IntegerField()
    user_name = models.CharField(max_length=_max_length)

    def __str__(self):
        return 'message_text = {}'.format(self.message_text)


class Topic(models.Model):
    topic_name = models.CharField(max_length=_max_length)
    topic_id = models.IntegerField()
    section_id = models.IntegerField()
    modification_date = models.DateTimeField('modification date')

    def __str__(self):
        return 'topic_name = {}'.format(self.topic_name)


class Section(models.Model):
    section_name = models.CharField(max_length=_max_length)
    section_id = models.IntegerField()

    def __str__(self):
        return 'section_name = {}'.format(self.section_name)