from django.core.management.base import BaseCommand
from django.utils import timezone
from messaging.utils.notifications import NotificationManager


class Command(BaseCommand):
    help = 'Clean up old read notifications'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep read notifications (default: 30)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        if dry_run:
            from messaging.models import Notification
            count = Notification.objects.filter(
                is_read=True,
                read_at__lt=cutoff_date
            ).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Would delete {count} notifications older than {days} days'
                )
            )
        else:
            deleted_count = NotificationManager.cleanup_old_notifications(days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} old notifications'
                )
            )
            
            if deleted_count == 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'No notifications found older than {days} days'
                    )
                )