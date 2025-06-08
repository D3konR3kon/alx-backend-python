import logging

from datetime import datetime, time
from django.http import JsonResponse
from django.http import JsonResponse
from collections import defaultdict
from datetime import datetime, timedelta

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler("request_logs.log")
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_entry)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       
        start_time = time(18, 0) 
        end_time = time(21, 0) 
        current_time = datetime.now().time()

        if not (start_time <= current_time <= end_time):
            return JsonResponse(
                {
                    "error": "Access to messaging is only allowed between 6PM and 9PM."
                },
                status=403
            )

        return self.get_response(request)



class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.message_log = defaultdict(list)
        self.limit = 5
        self.window = 60 

    def __call__(self, request):
        if request.method == 'POST' and '/send_message/' in request.path:
            ip = self.get_client_ip(request)
            now = time.time()

            recent_timestamps = [
                ts for ts in self.message_log[ip] if now - ts < self.window
            ]
            self.message_log[ip] = recent_timestamps

            if len(recent_timestamps) >= self.limit:
                return JsonResponse(
                    {"error": "Rate limit exceeded. You can only send 5 messages per minute."},
                    status=429
                )


            self.message_log[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Gets client IP address from request headers (supports proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
