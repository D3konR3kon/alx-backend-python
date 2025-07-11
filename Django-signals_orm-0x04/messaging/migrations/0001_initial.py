# Generated by Django 5.2.1 on 2025-06-14 16:14

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('is_online', models.BooleanField(default=False)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('conversation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('conversation_type', models.CharField(choices=[('direct', 'Direct Message'), ('group', 'Group Chat')], default='direct', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_conversations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conversation',
                'verbose_name_plural': 'Conversations',
                'db_table': 'conversations',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ConversationParticipant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('member', 'Member'), ('admin', 'Admin'), ('owner', 'Owner')], default='member', max_length=10)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('last_read_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_muted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_participants', to='messaging.conversation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_conversations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conversation Participant',
                'verbose_name_plural': 'Conversation Participants',
                'db_table': 'conversation_participants',
                'unique_together': {('conversation', 'user')},
            },
        ),
        migrations.AddField(
            model_name='conversation',
            name='participants',
            field=models.ManyToManyField(related_name='conversations', through='messaging.ConversationParticipant', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('message_type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('file', 'File'), ('audio', 'Audio'), ('video', 'Video'), ('system', 'System Message')], default='text', max_length=10)),
                ('message_body', models.TextField(blank=True)),
                ('file_attachment', models.FileField(blank=True, null=True, upload_to='message_files/')),
                ('is_edited', models.BooleanField(default=False)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='messaging.conversation')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='messaging.message')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'db_table': 'messages',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.CreateModel(
            name='MessageReaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reaction_type', models.CharField(choices=[('like', '👍'), ('love', '❤️'), ('laugh', '😂'), ('angry', '😠'), ('sad', '😢'), ('wow', '😮')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_reactions', to='messaging.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message Reaction',
                'verbose_name_plural': 'Message Reactions',
                'db_table': 'message_reactions',
                'unique_together': {('message', 'user', 'reaction_type')},
            },
        ),
        migrations.AddField(
            model_name='message',
            name='reactions',
            field=models.ManyToManyField(related_name='reacted_messages', through='messaging.MessageReaction', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('new_message', 'New Message'), ('mention', 'Mention'), ('reaction', 'Message Reaction'), ('conversation_invite', 'Conversation Invite'), ('system', 'System Notification')], max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('is_sent', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('related_conversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='messaging.conversation')),
                ('related_message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='messaging.message')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'db_table': 'notifications',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['recipient', '-created_at'], name='notificatio_recipie_2d3764_idx'), models.Index(fields=['recipient', 'is_read'], name='notificatio_recipie_583549_idx')],
            },
        ),
    ]
