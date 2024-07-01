from django.shortcuts import redirect
from django.contrib import messages
from social_core.exceptions import AuthCanceled  

class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):  # Catching specific authentication cancellation exception
            messages.error(request, "Authentication process canceled.")
            return redirect('accounts:home')  # Change 'home' to your desired redirect page
        return None