import logging
import time

logger_exception = logging.getLogger('middleware_exception')
logger_time = logging.getLogger('middleware_time')


class ExceptionMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        response = self._get_response(request)
        return response

    def process_exception(self, request, exception):
        logger_exception.critical((request.get_full_path(), request.content_params, exception))


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self._get_response(request)

        processing_time = time.time() - start_time
        logger_time.info((request.get_full_path(), f"Выполнение запроса: {processing_time} сек"))

        return response
